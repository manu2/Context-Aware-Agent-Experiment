#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances (all ordered pairs i,j) for a
large row-matrix, using only numpy + stdlib, under tight RAM/time limits.
"""
import numpy as np


def total_pairwise_distance(path="vectors.npy", block=1000):
    # (n x d) float32, C-contiguous straight from disk: ~32.8 MB for 8000x1024
    X = np.load(path)
    if X.dtype != np.float32:
        X = X.astype(np.float32, copy=False)
    if not X.flags.c_contiguous:
        X = np.ascontiguousarray(X)

    n = X.shape[0]

    # Squared row norms in float64, computed blockwise (no 32 MB temporary).
    sq = np.empty(n, dtype=np.float64)
    for i in range(0, n, block):
        blk = X[i:i + block]
        sq[i:i + block] = np.einsum("ij,ij->i", blk, blk, dtype=np.float64)

    total = 0.0
    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        A = X[i0:i1]                     # view, no copy
        si = sq[i0:i1][:, None]
        for j0 in range(i0, n, block):   # upper-triangular blocks only
            j1 = min(j0 + block, n)
            B = X[j0:j1]                 # view, no copy

            # Gram tile via BLAS sgemm  (<= 4 MB for 1000x1000 float32)
            G = A @ B.T

            # D2 = |a|^2 + |b|^2 - 2 a.b   in float64 (<= 8 MB)
            D2 = si + sq[j0:j1][None, :]
            D2 -= 2.0 * G
            del G
            np.maximum(D2, 0.0, out=D2)  # kill round-off negatives
            np.sqrt(D2, out=D2)

            s = float(D2.sum())          # pairwise-summed, float64
            del D2

            # diagonal tile: already contains both (i,j) and (j,i)
            # off-diagonal tile: mirror counts for the lower triangle
            total += s if i0 == j0 else 2.0 * s

    return total


if __name__ == "__main__":
    print("TOTAL_DIST:{:.6f}".format(total_pairwise_distance()))