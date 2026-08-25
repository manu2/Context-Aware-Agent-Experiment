#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between rows
of an 8,000 x 1,024 float32 matrix stored in 'vectors.npy'.

sum_{i,j} ||v_i - v_j||_2   (over all ordered pairs i,j, including i=j which contributes 0)

Uses only numpy and the standard library.
"""

import numpy as np


def main():
    # Load the data
    vectors = np.load('vectors.npy')

    # Work in float64 for numerical stability of the distance computation
    vectors = vectors.astype(np.float64, copy=False)

    n = vectors.shape[0]

    # Precompute squared norms of each row: ||v_i||^2
    sq_norms = np.einsum('ij,ij->i', vectors, vectors)

    total = 0.0

    # Process in blocks to avoid allocating a full n x n distance matrix at once,
    # which would require ~512MB+ for n=8000 in float64 (manageable but we chunk
    # to keep memory usage low and predictable).
    block_size = 500

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vectors[start:end]                     # shape (b, d)

        # Dot products between block rows and all rows: shape (b, n)
        dot = block @ vectors.T

        # Squared Euclidean distances: ||a||^2 + ||b||^2 - 2*a.b
        dist_sq = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dot

        # Numerical noise can produce tiny negative values; clip them to zero
        np.maximum(dist_sq, 0.0, out=dist_sq)

        dist = np.sqrt(dist_sq)

        total += dist.sum()

    print(f'TOTAL_DIST:{total}')


if __name__ == '__main__':
    main()