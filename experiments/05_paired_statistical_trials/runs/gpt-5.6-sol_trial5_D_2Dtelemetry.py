#!/usr/bin/env python3

import os

# Limit BLAS worker memory while retaining parallel matrix multiplication.
try:
    available_cpus = len(os.sched_getaffinity(0))
except AttributeError:
    available_cpus = os.cpu_count() or 1

thread_count = str(max(1, min(8, available_cpus)))
for variable in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ[variable] = thread_count

import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r")

    if vectors.shape != (8000, 1024):
        raise ValueError(
            f"Expected vectors.npy to have shape (8000, 1024), got {vectors.shape}"
        )
    if vectors.dtype != np.float32:
        raise ValueError(
            f"Expected vectors.npy to contain float32 values, got {vectors.dtype}"
        )

    n = vectors.shape[0]
    block_size = 384

    # Squared row norms, retained as float32 for fast SGEMM-based processing.
    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=False
    )

    total = 0.0

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vectors[start:end]
        block_norms = squared_norms[start:end]

        # Distances among rows in this block. This matrix already contains both
        # directions, so its sum is added once.
        distances = block @ block.T
        distances *= np.float32(-2.0)
        distances += block_norms[:, None]
        distances += block_norms[None, :]
        np.maximum(distances, np.float32(0.0), out=distances)
        np.sqrt(distances, out=distances)
        np.fill_diagonal(distances, np.float32(0.0))
        total += float(np.sum(distances, dtype=np.float64))
        del distances

        # Distances from this block to all later rows are computed once and
        # doubled to account for both (i, j) and (j, i).
        if end < n:
            later = vectors[end:]
            distances = block @ later.T
            distances *= np.float32(-2.0)
            distances += block_norms[:, None]
            distances += squared_norms[end:][None, :]
            np.maximum(distances, np.float32(0.0), out=distances)
            np.sqrt(distances, out=distances)
            total += 2.0 * float(np.sum(distances, dtype=np.float64))
            del distances

    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()