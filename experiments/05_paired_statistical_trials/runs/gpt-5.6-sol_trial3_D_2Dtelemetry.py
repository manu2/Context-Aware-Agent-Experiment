#!/usr/bin/env python3

import os

# Configure BLAS threading before importing NumPy.
try:
    available_cpus = len(os.sched_getaffinity(0))
except (AttributeError, OSError):
    available_cpus = os.cpu_count() or 1

blas_threads = str(min(8, available_cpus))
os.environ["OPENBLAS_NUM_THREADS"] = blas_threads
os.environ["MKL_NUM_THREADS"] = blas_threads
os.environ["OMP_NUM_THREADS"] = blas_threads
os.environ["VECLIB_MAXIMUM_THREADS"] = blas_threads

import numpy as np


def main():
    # Memory-map the 32 MB input instead of making an additional copy.
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024):
        raise ValueError(f"Expected shape (8000, 1024), got {vectors.shape}")
    if vectors.dtype != np.float32:
        raise ValueError(f"Expected float32 data, got {vectors.dtype}")

    n = vectors.shape[0]
    block_size = 512

    # ||x||^2 for every row, without creating a vectors**2 temporary.
    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=True
    )

    total = 0.0

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vectors[start:end]

        # Only compare this block with rows up through this block. Cross-block
        # distances are doubled; within-block distances already include both
        # ordered directions.
        distances = block @ vectors[:end].T
        distances *= np.float32(-2.0)
        distances += squared_norms[start:end, None]
        distances += squared_norms[None, :end]

        # Suppress small negative values caused by float32 roundoff.
        np.maximum(distances, np.float32(0.0), out=distances)
        np.sqrt(distances, out=distances)

        # Ensure self-distances are exactly zero.
        rows = np.arange(end - start)
        distances[rows, start + rows] = 0.0

        if start:
            total += 2.0 * distances[:, :start].sum(dtype=np.float64)

        total += distances[:, start:end].sum(dtype=np.float64)

    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()