#!/usr/bin/env python3
import os

# Limit BLAS threads to control memory usage while retaining parallelism.
_threads = str(min(4, os.cpu_count() or 1))
os.environ["OPENBLAS_NUM_THREADS"] = _threads
os.environ["MKL_NUM_THREADS"] = _threads
os.environ["OMP_NUM_THREADS"] = _threads
os.environ["VECLIB_MAXIMUM_THREADS"] = _threads

import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError(
            f"Expected an 8000x1024 float32 array, got "
            f"shape={vectors.shape}, dtype={vectors.dtype}"
        )

    n = vectors.shape[0]
    block_size = 1000

    # ||x-y||^2 = ||x||^2 + ||y||^2 - 2*x·y
    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=True
    )

    total = 0.0

    # Only compute the upper block triangle. Off-diagonal blocks are doubled
    # because the requested sum includes both (i,j) and (j,i).
    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        left = vectors[i0:i1]

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            right = vectors[j0:j1]

            distances = np.matmul(left, right.T)
            distances *= -2.0
            distances += squared_norms[i0:i1, None]
            distances += squared_norms[None, j0:j1]

            # Remove small negative values caused by float32 roundoff.
            np.maximum(distances, 0.0, out=distances)

            if i0 == j0:
                # Self-distances must be exactly zero.
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = np.sum(distances, dtype=np.float64)

            total += block_sum if i0 == j0 else 2.0 * block_sum

    print(f"TOTAL_DIST:{total:.10f}")


if __name__ == "__main__":
    main()