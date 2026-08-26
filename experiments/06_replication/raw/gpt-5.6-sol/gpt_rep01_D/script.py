#!/usr/bin/env python3

import os

# Limit BLAS worker memory while retaining parallel matrix multiplication.
os.environ["OPENBLAS_NUM_THREADS"] = "4"
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["VECLIB_MAXIMUM_THREADS"] = "4"

import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError(
            f"Expected an 8000 x 1024 float32 matrix, got "
            f"shape={vectors.shape}, dtype={vectors.dtype}"
        )

    n = vectors.shape[0]
    block_size = 512

    # Squared row norms, without constructing a matrix-sized temporary.
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    total = 0.0

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        a = vectors[i:i_end]
        a_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            b = vectors[j:j_end]

            # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a·b
            distances = a @ b.T
            distances *= -2.0
            distances += a_norms[:, None]
            distances += norms[j:j_end][None, :]

            # Remove small negative values caused by float32 roundoff.
            np.maximum(distances, 0.0, out=distances)
            np.sqrt(distances, out=distances)

            if i == j:
                # Self-distances are exactly zero. The full diagonal block
                # already contains both directions.
                np.fill_diagonal(distances, 0.0)
                total += float(np.sum(distances, dtype=np.float64))
            else:
                # Only the upper block was computed, so include its transpose.
                total += 2.0 * float(np.sum(distances, dtype=np.float64))

    print("TOTAL_DIST:" + format(total, ".17g"))


if __name__ == "__main__":
    main()