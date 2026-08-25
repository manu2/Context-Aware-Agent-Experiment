#!/usr/bin/env python3

import math
import numpy as np


FILE_NAME = "vectors.npy"
BLOCK_SIZE = 256


def main():
    # Memory-map the input so the entire matrix is not copied into RAM.
    vectors = np.load(FILE_NAME, mmap_mode="r")

    if vectors.shape != (8000, 1024):
        raise ValueError(f"Expected shape (8000, 1024), got {vectors.shape}")
    if vectors.dtype != np.float32:
        raise ValueError(f"Expected float32 data, got {vectors.dtype}")

    n = vectors.shape[0]

    # Compute squared row norms in small float64 blocks for numerical accuracy.
    norms = np.empty(n, dtype=np.float64)
    for start in range(0, n, BLOCK_SIZE):
        end = min(start + BLOCK_SIZE, n)
        block = np.asarray(vectors[start:end], dtype=np.float64)
        norms[start:end] = np.einsum(
            "ij,ij->i", block, block, optimize=True
        )

    partial_sums = []

    # Process only the upper block triangle. Off-diagonal blocks are doubled
    # because the requested sum includes both (i, j) and (j, i).
    for i_start in range(0, n, BLOCK_SIZE):
        i_end = min(i_start + BLOCK_SIZE, n)
        a = np.asarray(vectors[i_start:i_end], dtype=np.float64)
        norm_a = norms[i_start:i_end]

        for j_start in range(i_start, n, BLOCK_SIZE):
            j_end = min(j_start + BLOCK_SIZE, n)

            if j_start == i_start:
                b = a
            else:
                b = np.asarray(vectors[j_start:j_end], dtype=np.float64)

            norm_b = norms[j_start:j_end]

            # Reuse the Gram matrix allocation as the squared-distance matrix:
            # ||a-b||² = ||a||² + ||b||² - 2(a·b)
            distances = a @ b.T
            distances *= -2.0
            distances += norm_a[:, None]
            distances += norm_b[None, :]

            # Remove tiny negative values caused by floating-point roundoff.
            np.maximum(distances, 0.0, out=distances)

            if j_start == i_start:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))

            partial_sums.append(
                block_sum if j_start == i_start else 2.0 * block_sum
            )

    total = math.fsum(partial_sums)
    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()