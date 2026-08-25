#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between rows
of an 8000 x 1024 float32 matrix stored in 'vectors.npy'.

Only numpy and the standard library are used. Memory is kept low by
processing the data in row-blocks and reusing buffers, so that the
full 8000x8000 distance matrix (which would take ~512MB in float64
or ~256MB in float32) is never materialized at once.
"""

import sys
import numpy as np


def main():
    # Load the data (8000 x 1024 float32 -> ~32MB)
    vectors = np.load('vectors.npy')
    if vectors.dtype != np.float32:
        vectors = vectors.astype(np.float32)

    n, d = vectors.shape

    # Precompute squared norms of each row: shape (n,)
    sq_norms = np.einsum('ij,ij->i', vectors, vectors, dtype=np.float32)

    total = 0.0  # accumulate in double precision for accuracy

    # Choose a block size that keeps memory usage well within limits.
    # A block of size B produces a (B x n) intermediate matrix.
    # For n=8000, float32, B=1000 -> ~32MB per intermediate buffer.
    block_size = 1000

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vectors[start:end]          # (B, d) float32

        # dot[i, j] = <block_i, vectors_j>
        dot = block @ vectors.T             # (B, n) float32

        # dist_sq[i, j] = ||block_i||^2 + ||vectors_j||^2 - 2*dot[i, j]
        dist_sq = sq_norms[start:end, None] + sq_norms[None, :]
        dist_sq -= 2.0 * dot

        # Numerical safety: clip tiny negative values caused by float error
        np.maximum(dist_sq, 0.0, out=dist_sq)

        # In-place sqrt to avoid extra allocation
        np.sqrt(dist_sq, out=dist_sq)

        # Sum this block's contribution in double precision
        total += dist_sq.sum(dtype=np.float64)

        # Free references explicitly (helps GC under tight RAM limits)
        del dot, dist_sq, block

    print(f'TOTAL_DIST:{total}')


if __name__ == '__main__':
    main()