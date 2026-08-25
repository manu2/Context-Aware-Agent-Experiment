#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances between rows of 'vectors.npy'.

    S = sum_{i=1..n} sum_{j=1..n} ||v_i - v_j||_2      (ordered pairs, S = 2 * sum_{i<j})

Strategy
--------
Blocked Gram-matrix expansion:   ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b
so a block of the distance matrix is one BLAS GEMM call (fast, no giant temporaries).

Numerical care:
  * Work in float64; the float32 input is promoted once.
  * Mean-center the data first. Distances are translation-invariant, but centering
    shrinks ||v||^2, which is exactly the quantity that causes catastrophic
    cancellation in the identity above when points are close together.
  * Clip tiny negative squared distances (round-off) to 0 before sqrt.
  * Accumulate block partial sums with math.fsum (exact summation).

Only numpy + the standard library are used.
"""

import argparse
import math
import os
import sys
import time

import numpy as np


# ----------------------------------------------------------------------
# Core computation
# ----------------------------------------------------------------------
def total_pairwise_distance(X, block=512, verbose=False):
    """Return sum over ALL ordered pairs (i, j) of ||X[i] - X[j]||_2."""
    n = X.shape[0]
    if n < 2:
        return 0.0

    # Promote to float64 and center (translation-invariant, improves conditioning).
    Xc = np.array(X, dtype=np.float64, order='C', copy=True)
    Xc -= Xc.mean(axis=0, dtype=np.float64)

    # Squared norms of every row.
    sq = np.einsum('ij,ij->i', Xc, Xc)

    partials = []
    t0 = time.time()

    for start in range(0, n, block):
        stop = min(start + block, n)
        b = stop - start

        B = Xc[start:stop]              # (b, d)
        T = Xc[start:]                  # (n - start, d)  -> upper band only

        # d2[a, j] = sq[start+a] + sq[start+j] - 2 * B[a] . T[j]
        G = B @ T.T                     # (b, n-start), single GEMM
        G *= -2.0
        G += sq[start:stop, None]
        G += sq[None, start:]

        np.maximum(G, 0.0, out=G)       # kill -1e-12 round-off before sqrt
        np.sqrt(G, out=G)

        # G[:, :b]  -> the symmetric diagonal block: already contains both (i,j)
        #              and (j,i), so count it once.
        # G[:, b:]  -> strictly-upper band: count twice for the mirrored pairs.
        partials.append(float(G[:, :b].sum(dtype=np.float64)))
        if G.shape[1] > b:
            partials.append(2.0 * float(G[:, b:].sum(dtype=np.float64)))

        if verbose:
            done = stop / n
            sys.stderr.write(
                f"\r  blocks: {stop:6d}/{n} rows ({done:5.1%})  "
                f"{time.time() - t0:6.1f}s"
            )
            sys.stderr.flush()

    if verbose:
        sys.stderr.write("\n")

    return math.fsum(partials)


# ----------------------------------------------------------------------
# Brute-force reference (small n only) — used for self-verification
# ----------------------------------------------------------------------
def brute_force(X):
    Y = np.asarray(X, dtype=np.float64)
    total = 0.0
    for i in range(Y.shape[0]):
        d = np.sqrt(np.sum((Y - Y[i]) ** 2, axis=1))
        total += float(d.sum())
    return total


def self_test(seed=0):
    """Verify the blocked algorithm against an explicit O(n^2 d) loop."""
    rng = np.random.default_rng(seed)
    for n, d, blk in ((37, 13, 8), (128, 64, 50), (200, 5, 512)):
        A = rng.standard_normal((n, d)).astype(np.float32)
        A[:5] = A[0]                                   # duplicate rows -> zero distances
        fast, ref = total_pairwise_distance(A, block=blk), brute_force(A)
        rel = abs(fast - ref) / max(ref, 1e-30)
        print(f"  self-test n={n:4d} d={d:3d} block={blk:3d}: "
              f"rel.err={rel:.3e} {'OK' if rel < 1e-10 else 'FAIL'}",
              file=sys.stderr)
        if rel >= 1e-10:
            raise AssertionError("blocked algorithm disagrees with brute force")


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default="vectors.npy")
    ap.add_argument("--block", type=int, default=512,
                    help="rows per block (memory/speed trade-off)")
    ap.add_argument("--verbose", action="store_true", help="progress + timing to stderr")
    ap.add_argument("--self-test", action="store_true",
                    help="validate against brute force on small matrices, then exit")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    if not os.path.isfile(args.path):
        sys.exit(f"error: '{args.path}' not found")

    X = np.load(args.path, allow_pickle=False)
    if X.ndim != 2:
        sys.exit(f"error: expected a 2-D array, got shape {X.shape}")
    if not np.issubdtype(X.dtype, np.number):
        sys.exit(f"error: non-numeric dtype {X.dtype}")
    if not np.all(np.isfinite(X)):
        sys.exit("error: input contains NaN or Inf")

    if args.verbose:
        n, d = X.shape
        print(f"  loaded {args.path}: shape={X.shape} dtype={X.dtype}", file=sys.stderr)
        print(f"  pairs={n*n:,}  peak block RAM ~ "
              f"{args.block * n * 8 / 2**20:.0f} MiB", file=sys.stderr)

    t0 = time.time()
    total = total_pairwise_distance(X, block=args.block, verbose=args.verbose)
    if args.verbose:
        print(f"  elapsed: {time.time() - t0:.1f}s", file=sys.stderr)

    print(f"TOTAL_DIST:{total:.6f}")


if __name__ == "__main__":
    main()