#!/usr/bin/env python3
"""
Compute the sum of all pairwise Euclidean distances between rows of a
matrix stored in 'vectors.npy' (8000 x 1024 float32).

Uses the identity:
    ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * v_i . v_j

to avoid ever materializing an explicit (N, N, D) array of differences.
Only a (block_size, N) matrix of dot products is held in memory at a
time, keeping memory usage low regardless of N.

Only numpy and the standard library are used.
"""

import numpy as np


def compute_total_pairwise_distance(vectors_path: str = "vectors.npy",
                                     block_size: int = 500) -> float:
    # Load the matrix; keep it in float32 to save memory.
    X = np.load(vectors_path)
    if X.dtype != np.float32:
        X = X.astype(np.float32, copy=False)

    n_rows, n_cols = X.shape

    # Precompute squared norms of each row: ||v_i||^2
    # Using einsum avoids allocating an intermediate squared array of full size unnecessarily.
    sq_norms = np.einsum('ij,ij->i', X, X, dtype=np.float32)

    total = 0.0  # accumulate in float64 for numerical stability

    # Process rows in blocks to limit peak memory usage.
    for start in range(0, n_rows, block_size):
        end = min(start + block_size, n_rows)
        Xi = X[start:end]                     # shape (b, D)
        norms_i = sq_norms[start:end]          # shape (b,)

        # Dot products between block rows and all rows: shape (b, N)
        dots = Xi @ X.T

        # Squared distances via the norm identity.
        # sq_dist[k, j] = ||v_{start+k}||^2 + ||v_j||^2 - 2 * dot(v_{start+k}, v_j)
        sq_dist = norms_i[:, None] + sq_norms[None, :] - 2.0 * dots

        # Numerical noise can push tiny negative values (near-zero distances) below 0.
        np.maximum(sq_dist, 0, out=sq_dist)

        # Euclidean distances.
        dist = np.sqrt(sq_dist, dtype=np.float32)

        # Accumulate sum in float64 to reduce accumulation error.
        total += dist.sum(dtype=np.float64)

        # Explicitly drop references to help garbage collection of large temporaries.
        del dots, sq_dist, dist

    return total


def main():
    total_dist = compute_total_pairwise_distance("vectors.npy", block_size=500)
    print(f"TOTAL_DIST:{total_dist}")


if __name__ == "__main__":
    main()