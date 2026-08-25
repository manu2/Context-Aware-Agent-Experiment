#!/usr/bin/env python3

import numpy as np


def main():
    vectors = np.load("vectors.npy", allow_pickle=False)

    if vectors.shape != (8000, 1024):
        raise ValueError(f"Expected shape (8000, 1024), got {vectors.shape}")
    if vectors.dtype != np.float32:
        raise TypeError(f"Expected float32 data, got {vectors.dtype}")

    # Float64 reduces error in dot products and the accumulated total.
    vectors = np.ascontiguousarray(vectors, dtype=np.float64)
    squared_norms = np.einsum("ij,ij->i", vectors, vectors)

    block_size = 512
    n = vectors.shape[0]
    total = 0.0

    # Compute only the upper block triangle. Off-diagonal blocks are counted
    # twice because the requested sum includes both (i, j) and (j, i).
    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        a = vectors[i0:i1]
        norms_a = squared_norms[i0:i1]

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            b = vectors[j0:j1]
            norms_b = squared_norms[j0:j1]

            distances_sq = a @ b.T
            distances_sq *= -2.0
            distances_sq += norms_a[:, None]
            distances_sq += norms_b[None, :]

            # Remove tiny negative values caused by floating-point rounding.
            np.maximum(distances_sq, 0.0, out=distances_sq)

            if i0 == j0:
                # Self-distances are exactly zero.
                np.fill_diagonal(distances_sq, 0.0)

            np.sqrt(distances_sq, out=distances_sq)
            block_sum = float(np.sum(distances_sq, dtype=np.float64))

            total += block_sum if i0 == j0 else 2.0 * block_sum

    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()