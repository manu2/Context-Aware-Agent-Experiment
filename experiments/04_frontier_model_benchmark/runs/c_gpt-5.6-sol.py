#!/usr/bin/env python3

import os

# Limit BLAS thread memory usage under the 128 MB RAM constraint.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024):
        raise ValueError(f"Expected shape (8000, 1024), got {vectors.shape}")
    if vectors.dtype != np.float32:
        raise ValueError(f"Expected dtype float32, got {vectors.dtype}")

    # Blocks keep the distance matrix and float64 working copies small.
    block_size = 512
    n = vectors.shape[0]

    total = 0.0
    compensation = 0.0  # Kahan summation compensation.

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        xi = np.array(vectors[i:i_end], dtype=np.float64, order="C", copy=True)
        ni = np.einsum("ij,ij->i", xi, xi, optimize=False)

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)

            if j == i:
                xj = xi
                nj = ni
            else:
                xj = np.array(
                    vectors[j:j_end], dtype=np.float64, order="C", copy=True
                )
                nj = np.einsum("ij,ij->i", xj, xj, optimize=False)

            # Squared distances:
            # ||x-y||^2 = ||x||^2 + ||y||^2 - 2*x·y
            distances = xi @ xj.T
            distances *= -2.0
            distances += ni[:, None]
            distances += nj[None, :]
            np.maximum(distances, 0.0, out=distances)

            if j == i:
                # Eliminate tiny numerical residuals on self-distances.
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))

            # Off-diagonal blocks represent both (i,j) and (j,i).
            contribution = block_sum if j == i else 2.0 * block_sum

            # Compensated accumulation of block sums.
            adjusted = contribution - compensation
            updated = total + adjusted
            compensation = (updated - total) - adjusted
            total = updated

            del distances
            if j != i:
                del xj, nj

        del xi, ni

    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()