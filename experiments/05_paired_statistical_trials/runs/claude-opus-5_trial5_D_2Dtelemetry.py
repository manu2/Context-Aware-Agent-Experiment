#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between the rows of
an 8000 x 1024 float32 matrix stored in 'vectors.npy':

        TOTAL = sum_{i} sum_{j} || v_i - v_j ||_2

Only numpy + the standard library are used.

Strategy
--------
*  Use the Gram-matrix identity  ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b  so the
   heavy lifting is a BLAS matrix multiply (fast, multi-threaded).
*  Work on blocks of rows so that the 8000x8000 distance matrix (256 MB in
   float32) is never materialised -> memory stays well under 128 MB.
*  Only block pairs (i <= j) are evaluated; off-diagonal blocks are counted
   twice (symmetry), which halves the FLOP count.
*  The data is mean-centred first (distances are invariant under translation)
   which minimises ||a||^2 and therefore the catastrophic-cancellation error of
   the float32 dot products; the subtraction/accumulation itself is done in
   float64.
"""

import numpy as np


FILENAME = "vectors.npy"
BLOCK = 1000          # rows per block: 1000x1000 float64 buffer = 8 MB


def main():
    # ---- load (32.8 MB) -------------------------------------------------
    X = np.load(FILENAME)
    X = np.ascontiguousarray(X, dtype=np.float32)
    n, d = X.shape

    # ---- centre in place (distances unchanged, precision improved) ------
    mean = X.mean(axis=0, dtype=np.float64).astype(np.float32)
    X -= mean

    # ---- squared norms in float64 --------------------------------------
    sq = np.empty(n, dtype=np.float64)
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        blk = X[s:e].astype(np.float64)
        sq[s:e] = np.einsum('ij,ij->i', blk, blk)
        del blk

    # ---- reusable buffers ----------------------------------------------
    gbuf = np.empty((BLOCK, BLOCK), dtype=np.float32)   # 4 MB
    dbuf = np.empty((BLOCK, BLOCK), dtype=np.float64)   # 8 MB

    total = 0.0

    for i0 in range(0, n, BLOCK):
        i1 = min(i0 + BLOCK, n)
        Xi = X[i0:i1]
        sqi = sq[i0:i1][:, None]

        for j0 in range(i0, n, BLOCK):
            j1 = min(j0 + BLOCK, n)
            Xj = X[j0:j1]
            sqj = sq[j0:j1][None, :]

            a, b = i1 - i0, j1 - j0
            G = gbuf[:a, :b]
            np.matmul(Xi, Xj.T, out=G)          # BLAS sgemm

            D = dbuf[:a, :b]
            np.copyto(D, G)                     # promote to float64
            D *= -2.0
            D += sqi
            D += sqj

            if i0 == j0:
                np.fill_diagonal(D, 0.0)        # exact zeros on the diagonal

            np.maximum(D, 0.0, out=D)           # kill tiny negatives
            np.sqrt(D, out=D)

            s = float(D.sum(dtype=np.float64))
            total += s if i0 == j0 else 2.0 * s

    print("TOTAL_DIST:%.6f" % total)


if __name__ == "__main__":
    main()