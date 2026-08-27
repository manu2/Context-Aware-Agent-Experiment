#!/usr/bin/env python3

import os

# Limit BLAS memory usage while retaining parallel matrix multiplication.
os.environ["OPENBLAS_NUM_THREADS"] = "4"
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["VECLIB_MAXIMUM_THREADS"] = "4"

import math
import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError(
            f"Expected an (8000, 1024) float32 array, got "
            f"{vectors.shape} {vectors.dtype}"
        )

    n = vectors.shape[0]
    block_size = 500

    # Squared row norms without creating a matrix-sized temporary.
    norms = np.einsum(
        "ij,ij->i", vectors, vectors,
        dtype=np.float32,
        optimize=False,
    )

    distances = np.empty((block_size, block_size), dtype=np.float32)
    partial_sums = []

    # Compute only block pairs on/below the block diagonal.
    for i0 in range(0, n, block_size):
        i1 = i0 + block_size
        a = vectors[i0:i1]
        norm_a = norms[i0:i1]

        for j0 in range(0, i0 + 1, block_size):
            j1 = j0 + block_size
            b = vectors[j0:j1]

            # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a.b
            np.dot(a, b.T, out=distances)
            distances *= np.float32(-2.0)
            distances += norm_a[:, None]
            distances += norms[j0:j1][None, :]
            np.maximum(distances, np.float32(0.0), out=distances)

            if i0 == j0:
                np.fill_diagonal(distances, np.float32(0.0))

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))

            # Off-diagonal blocks represent both (i,j) and (j,i).
            partial_sums.append(block_sum if i0 == j0 else 2.0 * block_sum)

    total = math.fsum(partial_sums)
    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()