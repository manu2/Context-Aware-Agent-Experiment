#!/usr/bin/env python3

import numpy as np


def main():
    vectors = np.load("vectors.npy", allow_pickle=False)

    expected_shape = (8000, 1024)
    if vectors.shape != expected_shape:
        raise ValueError(
            f"Expected vectors.npy to have shape {expected_shape}, "
            f"but found {vectors.shape}"
        )

    # Float64 reduces cancellation error in the squared-distance identity:
    # ||a-b||^2 = ||a||^2 + ||b||^2 - 2(a @ b).
    vectors = np.asarray(vectors, dtype=np.float64, order="C")
    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float64
    )

    block_size = 512
    row_count = vectors.shape[0]
    total_distance = 0.0

    # Process only the upper block triangle. Off-diagonal blocks are doubled
    # because the requested sum includes both (i, j) and (j, i).
    for i in range(0, row_count, block_size):
        i_end = min(i + block_size, row_count)
        left = vectors[i:i_end]
        left_norms = squared_norms[i:i_end]

        for j in range(i, row_count, block_size):
            j_end = min(j + block_size, row_count)
            right = vectors[j:j_end]
            right_norms = squared_norms[j:j_end]

            distances = left @ right.T
            distances *= -2.0
            distances += left_norms[:, None]
            distances += right_norms[None, :]

            # Remove tiny negative values caused by floating-point rounding.
            np.maximum(distances, 0.0, out=distances)

            if i == j:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = np.sum(distances, dtype=np.float64)

            total_distance += block_sum if i == j else 2.0 * block_sum

    print(f"TOTAL_DIST:{total_distance:.17g}")


if __name__ == "__main__":
    main()