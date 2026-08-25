#!/usr/bin/env python3

import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r")

    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError(
            f"Expected an 8000 x 1024 float32 matrix, "
            f"got shape={vectors.shape}, dtype={vectors.dtype}"
        )

    n = vectors.shape[0]
    block_size = 1024

    # Compute squared row norms without creating a full-size temporary array.
    squared_norms = np.empty(n, dtype=np.float32)
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vectors[start:end]
        squared_norms[start:end] = np.einsum(
            "ij,ij->i", block, block, dtype=np.float32
        )

    total = 0.0

    # Only compute the upper block triangle. Off-diagonal blocks are doubled
    # because distance(i, j) == distance(j, i).
    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        xi = vectors[i0:i1]
        ni = squared_norms[i0:i1]

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            xj = vectors[j0:j1]
            nj = squared_norms[j0:j1]

            # Reuse the dot-product matrix as the squared-distance matrix:
            # ||x-y||^2 = ||x||^2 + ||y||^2 - 2*x·y
            distances = np.matmul(xi, xj.T)
            distances *= np.float32(-2.0)
            distances += ni[:, None]
            distances += nj[None, :]
            np.maximum(distances, np.float32(0.0), out=distances)

            if i0 == j0:
                # Ensure self-distances are exactly zero.
                np.fill_diagonal(distances, np.float32(0.0))

            np.sqrt(distances, out=distances)
            block_sum = np.sum(distances, dtype=np.float64)

            total += block_sum if i0 == j0 else 2.0 * block_sum

    print(f"TOTAL_DIST:{total:.10f}")


if __name__ == "__main__":
    main()