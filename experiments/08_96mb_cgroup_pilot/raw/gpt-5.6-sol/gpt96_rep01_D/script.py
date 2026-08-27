#!/usr/bin/env python3

import os

# Limit BLAS threads to avoid excessive memory use and oversubscription.
_threads = str(min(4, os.cpu_count() or 1))
os.environ["OPENBLAS_NUM_THREADS"] = _threads
os.environ["MKL_NUM_THREADS"] = _threads
os.environ["OMP_NUM_THREADS"] = _threads
os.environ["VECLIB_MAXIMUM_THREADS"] = _threads

import numpy as np


def main():
    # Memory-map the 32 MiB input instead of loading another full copy.
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError(
            f"Expected an (8000, 1024) float32 array, got "
            f"{vectors.shape} {vectors.dtype}"
        )

    n = vectors.shape[0]
    block_size = 500  # Exactly divides 8000; work matrix uses only 1 MiB.

    # Squared row norms without creating a matrix-sized temporary.
    norm2 = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=False
    )

    work = np.empty((block_size, block_size), dtype=np.float32)
    total = 0.0

    # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a·b
    # Only the block upper triangle is evaluated. Off-diagonal blocks are
    # doubled to account for both (i,j) and (j,i).
    for i in range(0, n, block_size):
        a = vectors[i:i + block_size]
        ni = norm2[i:i + block_size]

        for j in range(i, n, block_size):
            b = vectors[j:j + block_size]
            nj = norm2[j:j + block_size]

            np.matmul(a, b.T, out=work)
            np.multiply(work, -2.0, out=work)
            np.add(work, ni[:, None], out=work)
            np.add(work, nj[None, :], out=work)

            # Remove small negative values caused by float32 roundoff.
            np.maximum(work, 0.0, out=work)

            if i == j:
                # Distances from each row to itself are exactly zero.
                np.fill_diagonal(work, 0.0)

            np.sqrt(work, out=work)
            block_sum = float(np.sum(work, dtype=np.float64))

            total += block_sum if i == j else 2.0 * block_sum

    print(f"TOTAL_DIST:{total:.10f}")


if __name__ == "__main__":
    main()