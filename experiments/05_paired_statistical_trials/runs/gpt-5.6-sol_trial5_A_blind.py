#!/usr/bin/env python3

import math
import numpy as np


def main():
    loaded = np.load("vectors.npy", allow_pickle=False)

    if loaded.shape != (8000, 1024):
        raise ValueError(
            f"Expected vectors.npy to have shape (8000, 1024), got {loaded.shape}"
        )

    # Float64 reduces cancellation error in the squared-distance identity.
    vectors = np.ascontiguousarray(loaded, dtype=np.float64)
    del loaded

    squared_norms = np.einsum("ij,ij->i", vectors, vectors)
    block_size = 1024
    block_totals = []
    n = vectors.shape[0]

    # Process only the upper block triangle. Off-diagonal blocks are doubled
    # because the requested sum includes both (i, j) and (j, i).
    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        left = vectors[i0:i1]
        left_norms = squared_norms[i0:i1]

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            right = vectors[j0:j1]

            distances_squared = left @ right.T
            distances_squared *= -2.0
            distances_squared += left_norms[:, None]
            distances_squared += squared_norms[j0:j1][None, :]

            # Remove small negative values caused by floating-point rounding.
            np.maximum(distances_squared, 0.0, out=distances_squared)

            if i0 == j0:
                np.fill_diagonal(distances_squared, 0.0)

            np.sqrt(distances_squared, out=distances_squared)
            block_sum = float(np.sum(distances_squared, dtype=np.float64))

            block_totals.append(block_sum if i0 == j0 else 2.0 * block_sum)

    total_distance = math.fsum(block_totals)
    print(f"TOTAL_DIST:{total_distance:.17g}")


if __name__ == "__main__":
    main()