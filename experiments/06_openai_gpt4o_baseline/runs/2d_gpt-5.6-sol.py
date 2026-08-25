#!/usr/bin/env python3

import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)

    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError("vectors.npy must contain an 8000 x 1024 float32 matrix")

    # Squared row norms without creating a matrix-sized temporary.
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    block_size = 1024
    n = vectors.shape[0]
    total = 0.0

    # Compute only the upper block triangle. Off-diagonal blocks are doubled
    # to account for both (i, j) and (j, i).
    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        a = vectors[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            b = vectors[j:j_end]

            # ||a-b||² = ||a||² + ||b||² - 2*a·b
            distances = a @ b.T
            distances *= -2.0
            distances += norms[i:i_end, None]
            distances += norms[None, j:j_end]

            # Remove small negative values caused by float32 roundoff.
            np.maximum(distances, 0.0, out=distances)
            np.sqrt(distances, out=distances)

            if i == j:
                np.fill_diagonal(distances, 0.0)
                total += distances.sum(dtype=np.float64)
            else:
                total += 2.0 * distances.sum(dtype=np.float64)

            del distances

    print(f"TOTAL_DIST:{total:.10f}")


if __name__ == "__main__":
    main()