#!/usr/bin/env python3

import math
import numpy as np


def main() -> None:
    path = "vectors.npy"
    block_size = 512

    vectors = np.load(path, allow_pickle=False)

    if vectors.shape != (8000, 1024):
        raise ValueError(
            f"Expected vectors.npy to have shape (8000, 1024), "
            f"but found {vectors.shape}"
        )
    if vectors.dtype != np.float32:
        raise ValueError(
            f"Expected vectors.npy to contain float32 values, "
            f"but found {vectors.dtype}"
        )
    if not np.isfinite(vectors).all():
        raise ValueError("vectors.npy contains NaN or infinite values")

    # Float64 reduces cancellation error in:
    # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a·b
    vectors = np.asarray(vectors, dtype=np.float64, order="C")
    row_norms_sq = np.einsum("ij,ij->i", vectors, vectors)

    n = vectors.shape[0]
    partial_sums = []

    # Process only the upper block triangle. Off-diagonal blocks are doubled
    # because the requested sum includes both (i, j) and (j, i).
    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            right = vectors[j:j_end]

            distances_sq = left @ right.T
            distances_sq *= -2.0
            distances_sq += row_norms_sq[i:i_end, None]
            distances_sq += row_norms_sq[None, j:j_end]

            # Remove small negative values caused by floating-point rounding.
            np.maximum(distances_sq, 0.0, out=distances_sq)

            if i == j:
                # Self-distances must be exactly zero.
                np.fill_diagonal(distances_sq, 0.0)

            np.sqrt(distances_sq, out=distances_sq)
            block_sum = float(np.sum(distances_sq, dtype=np.float64))

            partial_sums.append(block_sum if i == j else 2.0 * block_sum)

    total = math.fsum(partial_sums)
    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()