#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between the rows of
the matrix stored in 'vectors.npy':

        S = sum_{i=0..n-1} sum_{j=0..n-1} || v_i - v_j ||_2

(Every unordered pair is counted twice; the diagonal contributes zero.)

Only numpy + the standard library are used.

Method
------
    ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 <v_i, v_j>

so a block of the distance matrix is obtained from one matrix product, which
NumPy hands to a multithreaded BLAS.  The matrix is traversed in row blocks
(only the upper block-triangle) so memory stays at O(block^2) instead of
O(n^2), and the result is doubled at the end.
"""

import argparse
import math
import os
import sys
import time

import numpy as np

DEFAULT_FILE = "vectors.npy"
DEFAULT_BLOCK = 1024          # rows per block -> 1024*1024*8 B = 8 MB per tile


# --------------------------------------------------------------------------- #
# core computation
# --------------------------------------------------------------------------- #
def total_pairwise_distance(X, block=DEFAULT_BLOCK, verbose=False):
    """
    Sum of ||x_i - x_j||_2 over ALL ordered pairs (i, j), i.e. 2 * sum_{i<j}.

    Parameters
    ----------
    X : (n, d) ndarray
    block : int, rows per tile
    """
    X = np.ascontiguousarray(X, dtype=np.float64)   # float64 for accuracy
    n = X.shape[0]
    if n < 2:
        return 0.0

    # squared norms of every row, computed once
    sq = np.einsum("ij,ij->i", X, X)

    partials = []           # per-tile sums, combined exactly at the end
    t0 = time.time()

    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        Xi, sqi = X[i0:i1], sq[i0:i1]

        for j0 in range(i0, n, block):            # upper block-triangle only
            j1 = min(j0 + block, n)
            Xj, sqj = X[j0:j1], sq[j0:j1]

            # squared distances for this tile
            d2 = Xi @ Xj.T                        # <- the expensive part (BLAS)
            d2 *= -2.0
            d2 += sqi[:, None]
            d2 += sqj[None, :]

            np.maximum(d2, 0.0, out=d2)           # kill round-off negatives
            np.sqrt(d2, out=d2)

            if i0 == j0:
                # diagonal tile: full tile sum = 2 * (strict upper part),
                # since the diagonal entries are exactly 0.
                partials.append(0.5 * float(d2.sum()))
            else:
                partials.append(float(d2.sum()))

        if verbose:
            done = i1 / n
            print(f"  ... {i1}/{n} rows ({done:6.1%}) "
                  f"elapsed {time.time() - t0:6.1f}s", file=sys.stderr)

    upper_sum = math.fsum(partials)               # sum over i < j
    return 2.0 * upper_sum                        # ordered pairs


# --------------------------------------------------------------------------- #
# self-test against a brute-force reference
# --------------------------------------------------------------------------- #
def _selftest():
    rng = np.random.default_rng(0)
    for n, d in ((1, 5), (2, 3), (37, 11), (200, 64)):
        A = rng.standard_normal((n, d)).astype(np.float32)
        ref = 0.0
        for i in range(n):                        # naive O(n^2 d) reference
            diff = A.astype(np.float64) - A[i].astype(np.float64)
            ref += np.sqrt((diff * diff).sum(axis=1)).sum()
        got = total_pairwise_distance(A, block=16)
        rel = abs(got - ref) / max(ref, 1e-12)
        assert rel < 1e-10, f"selftest failed n={n} d={d}: {got} vs {ref}"
        print(f"  ok  n={n:4d} d={d:3d}  rel.err={rel:.2e}")
    print("SELFTEST: PASS")


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=DEFAULT_FILE,
                    help=f"input .npy file (default: {DEFAULT_FILE})")
    ap.add_argument("--block", type=int, default=DEFAULT_BLOCK,
                    help=f"rows per tile (default: {DEFAULT_BLOCK})")
    ap.add_argument("--verbose", action="store_true", help="progress to stderr")
    ap.add_argument("--selftest", action="store_true",
                    help="verify against brute force on small inputs and exit")
    args = ap.parse_args()

    if args.selftest:
        _selftest()
        return 0

    if not os.path.exists(args.path):
        print(f"error: '{args.path}' not found", file=sys.stderr)
        return 1

    # mmap keeps the 31 MB file off the heap until it is cast below
    X = np.load(args.path, mmap_mode="r")
    if X.ndim != 2:
        print(f"error: expected a 2-D array, got shape {X.shape}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"loaded {args.path}: shape={X.shape} dtype={X.dtype}", file=sys.stderr)

    t0 = time.time()
    total = total_pairwise_distance(X, block=args.block, verbose=args.verbose)
    if args.verbose:
        n = X.shape[0]
        print(f"done in {time.time() - t0:.1f}s "
              f"({n * (n - 1) // 2:,} unordered pairs)", file=sys.stderr)

    print(f"TOTAL_DIST:{total:.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())