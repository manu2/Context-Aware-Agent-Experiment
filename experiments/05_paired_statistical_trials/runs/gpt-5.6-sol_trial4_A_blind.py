#!/usr/bin/env python3

import math
import numpy as np


FILE_NAME = "vectors.npy"
EXPECTED_SHAPE = (8000, 1024)
BLOCK_SIZE = 1024


def main():
    raw = np.load(FILE_NAME, mmap_mode="r", allow_pickle=False)

    if raw.shape != EXPECTED_SHAPE:
        raise ValueError(
            f"Expected an array of shape {EXPECTED_SHAPE}, got {raw.shape}"
        )
    if raw.dtype != np.float32:
        raise TypeError(f"Expected float32 data, got {raw.dtype}")

    # Float64 reduces cancellation error in:
    # ||x-y||^2 = ||x||^2 + ||y||^2 - 2*x·y
    vectors = np.array(raw, dtype=np.float64, order="C", copy=True)
    squared_norms = np.einsum("ij,ij->i", vectors, vectors)

    n = vectors.shape[0]
    partial_sums = []

    # Process only the upper block triangle. Off-diagonal blocks are doubled
    # because the requested sum includes both (i, j) and (j, i).
    for i0 in range(0, n, BLOCK_SIZE):
        i1 = min(i0 + BLOCK_SIZE, n)
        left = vectors[i0:i1]

        for j0 in range(i0, n, BLOCK_SIZE):
            j1 = min(j0 + BLOCK_SIZE, n)
            right = vectors[j0:j1]

            distances_squared = left @ right.T
            distances_squared *= -2.0
            distances_squared += squared_norms[i0:i1, None]
            distances_squared += squared_norms[None, j0:j1]

            # Remove small negative values caused by floating-point rounding.
            np.maximum(distances_squared, 0.0, out=distances_squared)

            if i0 == j0:
                # Distances of rows to themselves are exactly zero.
                np.fill_diagonal(distances_squared, 0.0)

            np.sqrt(distances_squared, out=distances_squared)
            block_sum = float(np.sum(distances_squared, dtype=np.float64))

            partial_sums.append(block_sum if i0 == j0 else 2.0 * block_sum)

    total_distance = math.fsum(partial_sums)
    print(f"TOTAL_DIST:{total_distance:.17g}")


if __name__ == "__main__":
    main()