#!/usr/bin/env python3

import os

# Limit BLAS worker count to stay within the 128 MB memory limit.
for variable in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "BLIS_NUM_THREADS",
):
    os.environ[variable] = "4"

import math
import numpy as np


def main() -> None:
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024):
        raise ValueError(f"Expected shape (8000, 1024), got {vectors.shape}")
    if vectors.dtype != np.float32:
        raise ValueError(f"Expected float32 data, got {vectors.dtype}")

    n = vectors.shape[0]
    block_size = 1000  # Divides 8000 exactly; work matrix uses about 4 MB.

    squared_norms = np.empty(n, dtype=np.float32)
    for start in range(0, n, block_size):
        end = start + block_size
        block = vectors[start:end]
        np.einsum(
            "ij,ij->i",
            block,
            block,
            out=squared_norms[start:end],
            optimize=False,
        )

    work = np.empty((block_size, block_size), dtype=np.float32)
    partial_sums = []

    # Only calculate block pairs with j >= i. Off-diagonal blocks are doubled
    # because the requested sum includes both (i, j) and (j, i).
    for i_start in range(0, n, block_size):
        i_end = i_start + block_size
        a = vectors[i_start:i_end]
        a_norms = squared_norms[i_start:i_end]

        for j_start in range(i_start, n, block_size):
            j_end = j_start + block_size
            b = vectors[j_start:j_end]
            b_norms = squared_norms[j_start:j_end]

            # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a·b
            np.matmul(a, b.T, out=work)
            work *= np.float32(-2.0)
            work += a_norms[:, None]
            work += b_norms[None, :]

            # Clamp small negative values caused by float32 roundoff.
            np.maximum(work, np.float32(0.0), out=work)
            np.sqrt(work, out=work)

            if i_start == j_start:
                # Self-distances are mathematically zero.
                np.fill_diagonal(work, np.float32(0.0))
                partial_sums.append(float(np.sum(work, dtype=np.float64)))
            else:
                partial_sums.append(
                    2.0 * float(np.sum(work, dtype=np.float64))
                )

    total = math.fsum(partial_sums)
    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()