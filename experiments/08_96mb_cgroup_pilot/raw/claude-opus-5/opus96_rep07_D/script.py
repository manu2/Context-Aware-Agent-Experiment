#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between the rows of
an 8,000 x 1,024 float32 matrix stored in 'vectors.npy'.

    S = sum_{i,j} ||v_i - v_j||_2      (all ordered pairs, diagonal = 0)

Strategy
--------
The full 8000x8000 distance matrix would need 256 MB (float32), so we never
materialize it.  Instead we tile the computation:

    ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a.b

For each pair of row-blocks (I, J) with I <= J we compute the Gram block
A_I @ A_J^T with a single BLAS sgemm call (fast, multi-threaded), turn it into
distances in place, and accumulate the sum in float64.  Only the upper-triangular
block pairs are computed; off-diagonal contributions are doubled by symmetry.

Numerical care
--------------
* The data is mean-centered first (this does not change any distance) which
  shrinks ||v||^2 relative to the pairwise distances and therefore reduces the
  catastrophic-cancellation error of the a.b expansion.
* Squared norms are accumulated in float64.
* Negative values caused by round-off are clipped to 0 before the sqrt.
* All block sums are accumulated with a float64 accumulator.

Memory: data 32 MB + one 1000x1000 float32 tile (4 MB) + scratch  ->  well under 96 MB.
Only numpy + stdlib are used.
"""

import os

# Make sure BLAS is allowed to use every core (only set if the user hasn't).
_ncpu = str(os.cpu_count() or 1)
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, _ncpu)

import numpy as np


FILENAME = "vectors.npy"
BLOCK = 1000          # rows per tile -> 1000x1000 float32 tile = 4 MB


def load_float32(path):
    """Load the matrix as a contiguous float32 array without doubling memory."""
    mm = np.load(path, mmap_mode="r")
    n, d = mm.shape
    if mm.dtype == np.float32:
        A = np.empty((n, d), dtype=np.float32)
        step = max(1, (1 << 22) // (d * 4))     # ~4 MB per copy chunk
        for s in range(0, n, step):
            A[s:s + step] = mm[s:s + step]
    else:                                        # convert in chunks
        A = np.empty((n, d), dtype=np.float32)
        step = max(1, (1 << 22) // (d * 8))
        for s in range(0, n, step):
            A[s:s + step] = mm[s:s + step].astype(np.float32, copy=False)
    del mm
    return A


def main():
    A = load_float32(FILENAME)
    n, d = A.shape

    # ---- center the data (distances are invariant) -------------------------
    mean = A.mean(axis=0, dtype=np.float64).astype(np.float32)
    for s in range(0, n, BLOCK):
        A[s:s + BLOCK] -= mean
    del mean

    # ---- squared norms (float64 accumulation, stored as float32) -----------
    sq = np.empty(n, dtype=np.float32)
    for s in range(0, n, BLOCK):
        blk = A[s:s + BLOCK]
        sq[s:s + BLOCK] = np.einsum("ij,ij->i", blk, blk, dtype=np.float64)

    starts = list(range(0, n, BLOCK))
    # reusable tile buffer (largest possible tile)
    tile = np.empty((BLOCK, BLOCK), dtype=np.float32)

    total = 0.0
    for bi, si in enumerate(starts):
        ei = min(si + BLOCK, n)
        Ai = A[si:ei]
        sqi = sq[si:ei].reshape(-1, 1)
        for sj in starts[bi:]:
            ej = min(sj + BLOCK, n)
            Aj = A[sj:ej]
            G = tile[:ei - si, :ej - sj]

            # G = -2 * Ai @ Aj^T   (single BLAS sgemm)
            np.dot(Ai, Aj.T, out=G)
            G *= -2.0
            G += sqi
            G += sq[sj:ej]                 # broadcast over rows
            np.maximum(G, 0.0, out=G)      # kill round-off negatives
            np.sqrt(G, out=G)

            s = float(np.sum(G, dtype=np.float64))
            total += s if si == sj else 2.0 * s

    print("TOTAL_DIST:%.6f" % total)


if __name__ == "__main__":
    main()