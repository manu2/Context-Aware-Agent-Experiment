#!/usr/bin/env python3

import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r")

    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError(
            f"Expected an (8000, 1024) float32 array, got "
            f"shape={vectors.shape}, dtype={vectors.dtype}"
        )

    n = vectors.shape[0]
    block_size = 1000

    # Squared row norms, computed without creating a full-sized temporary.
    norms = np.empty(n, dtype=np.float32)
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vectors[start:end]
        norms[start:end] = np.einsum(
            "ij,ij->i", block, block, dtype=np.float32, optimize=True
        )

    total = 0.0

    # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a·b.
    # Only upper block pairs are evaluated; off-diagonal blocks are doubled.
    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        a = vectors[i0:i1]

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            b = vectors[j0:j1]

            distances = np.matmul(a, b.T)
            distances *= -2.0
            distances += norms[i0:i1, None]
            distances += norms[None, j0:j1]

            # Remove small negative values caused by floating-point roundoff.
            np.maximum(distances, 0.0, out=distances)

            if i0 == j0:
                # Distances from each vector to itself are exactly zero.
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = distances.sum(dtype=np.float64)

            total += float(block_sum) if i0 == j0 else 2.0 * float(block_sum)

    print("TOTAL_DIST:" + format(total, ".17g"))


if __name__ == "__main__":
    main()