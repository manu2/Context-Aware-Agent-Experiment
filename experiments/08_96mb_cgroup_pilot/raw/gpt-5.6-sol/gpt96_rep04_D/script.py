#!/usr/bin/env python3

import os

# Limit BLAS thread count to control memory usage while retaining parallelism.
_threads = str(min(4, os.cpu_count() or 1))
for _name in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ[_name] = _threads

import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r")

    if vectors.shape != (8000, 1024):
        raise ValueError(f"Expected shape (8000, 1024), got {vectors.shape}")
    if vectors.dtype != np.float32:
        raise ValueError(f"Expected float32 data, got {vectors.dtype}")

    n = vectors.shape[0]
    block_size = 256

    # Compute squared row norms without creating a matrix-sized temporary.
    norms_sq = np.empty(n, dtype=np.float32)
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vectors[start:end]
        norms_sq[start:end] = np.einsum(
            "ij,ij->i", block, block, optimize=False
        )

    total = 0.0

    # Process only the upper block triangle. Off-diagonal blocks are doubled
    # because the requested sum includes both (i, j) and (j, i).
    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        a = vectors[i0:i1]
        a_norms = norms_sq[i0:i1]

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            b = vectors[j0:j1]

            # Reuse the dot-product matrix as the squared-distance matrix:
            # ||a-b||² = ||a||² + ||b||² - 2(a·b)
            distances = np.matmul(a, b.T)
            np.multiply(distances, -2.0, out=distances)
            distances += a_norms[:, None]
            distances += norms_sq[j0:j1][None, :]
            np.maximum(distances, 0.0, out=distances)

            if i0 == j0:
                # Eliminate floating-point residuals for self-distances.
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = distances.sum(dtype=np.float64)

            total += block_sum if i0 == j0 else 2.0 * block_sum

    print(f"TOTAL_DIST:{total:.10f}")


if __name__ == "__main__":
    main()