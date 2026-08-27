#!/usr/bin/env python3

import numpy as np


def main() -> None:
    vectors = np.load("vectors.npy", mmap_mode="r")

    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError(
            f"Expected an 8000 x 1024 float32 matrix, "
            f"got shape={vectors.shape}, dtype={vectors.dtype}"
        )

    # Squared row norms, retained as float32 so block calculations remain
    # memory-efficient and use fast single-precision matrix multiplication.
    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=True
    )

    # 500 divides 8000 exactly. The reusable work array consumes only 1 MB.
    block_size = 500
    work = np.empty((block_size, block_size), dtype=np.float32)
    total = 0.0

    for i in range(0, vectors.shape[0], block_size):
        a = vectors[i : i + block_size]
        norms_a = squared_norms[i : i + block_size]

        for j in range(i, vectors.shape[0], block_size):
            b = vectors[j : j + block_size]
            norms_b = squared_norms[j : j + block_size]

            # ||a-b||^2 = ||a||^2 + ||b||^2 - 2(a dot b)
            np.dot(a, b.T, out=work)
            work *= -2.0
            work += norms_a[:, None]
            work += norms_b[None, :]

            # Suppress small negative values caused by float32 roundoff.
            np.maximum(work, 0.0, out=work)
            np.sqrt(work, out=work)

            if i == j:
                # This block already contains both ordered directions.
                np.fill_diagonal(work, 0.0)
                total += np.sum(work, dtype=np.float64)
            else:
                # Account for both (i,j) and (j,i).
                total += 2.0 * np.sum(work, dtype=np.float64)

    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()