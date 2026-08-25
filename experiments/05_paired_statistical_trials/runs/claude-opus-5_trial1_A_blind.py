#!/usr/bin/env python3
"""
Total sum of all pairwise Euclidean distances among the rows of 'vectors.npy'.

    TOTAL_DIST = sum_{i=0}^{N-1} sum_{j=0}^{N-1} ||v_i - v_j||_2

Note this is the *ordered* double sum as specified: every unordered pair {i,j}
is counted twice and the i == j terms contribute 0, so it equals
2 * sum_{i<j} ||v_i - v_j||.  The unique-pair value is also reported on stderr.

Dependencies: numpy + Python standard library only.
"""

import math
import os
import sys
import time

import numpy as np

PATH = sys.argv[1] if len(sys.argv) > 1 else "vectors.npy"
BLOCK = 512          # rows of the distance matrix materialised at once


# --------------------------------------------------------------------------- #
# Core computation
# --------------------------------------------------------------------------- #
def total_pairwise_distance(X, block=BLOCK, progress=True):
    """
    Sum over ALL ordered pairs (i, j) of ||X[i] - X[j]||_2.

    Uses ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b, one GEMM per row-block.
    Everything is done in float64; per-block partial sums are combined with
    math.fsum so the final accumulation is exact to the last ulp.
    """
    n = X.shape[0]
    # Promote once to float64: 8000 x 1024 x 8 B = 65 MB. Contiguous -> fast GEMM.
    Xd = np.ascontiguousarray(X, dtype=np.float64)

    # Squared norms of every row (float64, computed without a temporary).
    sq = np.einsum("ij,ij->i", Xd, Xd)

    partials = []
    t0 = time.time()
    for start in range(0, n, block):
        stop = min(start + block, n)
        b = stop - start

        # G = -2 * Xblock @ X.T   -> shape (b, n), the only big temporary.
        G = Xd[start:stop] @ Xd.T
        G *= -2.0
        G += sq[start:stop, None]      # broadcast row norms
        G += sq[None, :]               # broadcast column norms

        # Round-off can push exact/near-zero entries slightly negative.
        np.maximum(G, 0.0, out=G)
        np.sqrt(G, out=G)

        # Force the true diagonal to exactly zero (self-distances).
        d = np.arange(b)
        G[d, start + d] = 0.0

        partials.append(G.sum(dtype=np.float64))

        if progress:
            done = stop / n
            sys.stderr.write(
                "\r  block %5d-%5d  (%5.1f%%)  %6.1fs" % (start, stop, 100 * done, time.time() - t0)
            )
            sys.stderr.flush()
    if progress:
        sys.stderr.write("\n")

    return math.fsum(partials)


# --------------------------------------------------------------------------- #
# Independent self-check on a random sub-block (direct differences, no Gram trick)
# --------------------------------------------------------------------------- #
def selfcheck(X, m=192, seed=0):
    n = X.shape[0]
    m = min(m, n)
    rng = np.random.default_rng(seed)
    idx = rng.choice(n, size=m, replace=False)
    S = np.ascontiguousarray(X[idx], dtype=np.float64)

    # Brute force: (m, m, d) differences, m=192 -> ~283 MB peak, done row by row.
    ref = 0.0
    rows = []
    for i in range(m):
        diff = S - S[i]
        rows.append(np.sqrt(np.einsum("ij,ij->i", diff, diff)).sum())
    ref = math.fsum(rows)

    fast = total_pairwise_distance(S, block=64, progress=False)
    rel = abs(fast - ref) / ref if ref > 0 else abs(fast - ref)
    return ref, fast, rel


def main():
    if not os.path.exists(PATH):
        sys.stderr.write("ERROR: '%s' not found.\n" % PATH)
        return 1

    X = np.load(PATH, mmap_mode="r")
    if X.ndim != 2:
        sys.stderr.write("ERROR: expected a 2-D array, got shape %r\n" % (X.shape,))
        return 1

    n, d = X.shape
    sys.stderr.write("Loaded %s: shape=%s dtype=%s (%.1f MB)\n"
                     % (PATH, X.shape, X.dtype, X.size * X.itemsize / 1e6))

    # --- validation -------------------------------------------------------- #
    ref, fast, rel = selfcheck(X)
    sys.stderr.write("Self-check on 192-row subset: direct=%.6f gram=%.6f rel.err=%.3e\n"
                     % (ref, fast, rel))
    if not (rel < 1e-9):
        sys.stderr.write("WARNING: self-check relative error is unexpectedly large.\n")

    # --- full computation -------------------------------------------------- #
    t0 = time.time()
    total = total_pairwise_distance(X)
    elapsed = time.time() - t0

    sys.stderr.write("N=%d D=%d  ordered pairs=%d  elapsed=%.1fs\n"
                     % (n, d, n * n, elapsed))
    sys.stderr.write("Unique-pair sum (i<j) = %.6f\n" % (total / 2.0))
    sys.stderr.write("Mean pairwise distance = %.6f\n"
                     % (total / (n * (n - 1)) if n > 1 else 0.0))

    print("TOTAL_DIST:%.6f" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())