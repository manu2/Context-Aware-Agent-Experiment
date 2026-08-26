#!/usr/bin/env python3

import numpy as np


def main():
    # Memory-map the input so it is not duplicated in RAM.
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    expected_shape = (8000, 1024)
    if vectors.shape != expected_shape:
        raise ValueError(
            f"Expected vectors.npy to have shape {expected_shape}, "
            f"got {vectors.shape}"
        )
    if vectors.dtype != np.float32:
        raise TypeError(
            f"Expected vectors.npy to contain float32 data, got {vectors.dtype}"
        )

    n = vectors.shape[0]
    block_size = 512

    # ||x-y||² = ||x||² + ||y||² - 2*x·y
    squared_norms = np.empty(n, dtype=np.float32)
    for start in range(0, n, block_size):
        stop = min(start + block_size, n)
        block = vectors[start:stop]
        np.einsum(
            "ij,ij->i",
            block,
            block,
            out=squared_norms[start:stop],
            optimize=True,
        )

    total = 0.0

    # Only process the upper block triangle. Off-diagonal blocks are counted
    # twice to include both (i, j) and (j, i).
    for i_start in range(0, n, block_size):
        i_stop = min(i_start + block_size, n)
        x_i = vectors[i_start:i_stop]
        norm_i = squared_norms[i_start:i_stop]

        for j_start in range(i_start, n, block_size):
            j_stop = min(j_start + block_size, n)
            x_j = vectors[j_start:j_stop]
            norm_j = squared_norms[j_start:j_stop]

            # The result remains float32, keeping peak memory well below 128 MB.
            distances = x_i @ x_j.T
            distances *= -2.0
            distances += norm_i[:, None]
            distances += norm_j[None, :]

            # Remove small negative values caused by floating-point rounding.
            np.maximum(distances, 0.0, out=distances)

            if i_start == j_start:
                # Self-distances are exactly zero.
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = np.sum(distances, dtype=np.float64)

            total += block_sum if i_start == j_start else 2.0 * block_sum

    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()