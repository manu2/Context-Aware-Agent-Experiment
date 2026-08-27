#!/usr/bin/env python3

import math
import numpy as np


def main() -> None:
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024):
        raise ValueError(f"Expected shape (8000, 1024), got {vectors.shape}")
    if vectors.dtype != np.float32:
        raise TypeError(f"Expected float32 data, got {vectors.dtype}")

    # Squared row norms. Pairwise squared distances are computed as:
    # ||x-y||² = ||x||² + ||y||² - 2*x·y
    squared_norms = np.einsum("ij,ij->i", vectors, vectors)

    block_size = 512
    n = vectors.shape[0]
    partial_sums = []

    # Only process the upper block triangle. Off-diagonal blocks are doubled
    # because the requested sum includes both (i, j) and (j, i).
    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        x = np.asarray(vectors[i0:i1])

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            y = np.asarray(vectors[j0:j1])

            # Reuse the dot-product array as the squared-distance array.
            distances = x @ y.T
            distances *= -2.0
            distances += squared_norms[i0:i1, None]
            distances += squared_norms[None, j0:j1]

            # Remove small negative values caused by floating-point rounding.
            np.maximum(distances, 0.0, out=distances)

            if i0 == j0:
                # Self-distances are exactly zero.
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))

            partial_sums.append(block_sum if i0 == j0 else 2.0 * block_sum)

    total = math.fsum(partial_sums)
    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()