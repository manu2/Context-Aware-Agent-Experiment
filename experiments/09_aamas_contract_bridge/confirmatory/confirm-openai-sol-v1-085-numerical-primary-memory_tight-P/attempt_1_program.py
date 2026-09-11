import os

for name in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "BLIS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[name] = "1"

import math
import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r")
    n, _ = vectors.shape
    block_size = 500

    squared_norms = np.empty(n, dtype=np.float64)
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = np.asarray(vectors[start:end], dtype=np.float64)
        squared_norms[start:end] = np.einsum(
            "ij,ij->i", block, block, optimize=True
        )

    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = np.asarray(vectors[i:i_end], dtype=np.float64)
        left_norms = squared_norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)

            if j == i:
                right = left
            else:
                right = np.asarray(vectors[j:j_end], dtype=np.float64)

            distances = left @ right.T
            distances *= -2.0
            distances += left_norms[:, None]
            distances += squared_norms[j:j_end][None, :]
            np.maximum(distances, 0.0, out=distances)

            if j == i:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            subtotal = float(np.sum(distances, dtype=np.float64))

            if j != i:
                subtotal *= 2.0

            partial_sums.append(subtotal)

    total = math.fsum(partial_sums)
    print("TOTAL:" + format(total, ".17g"))


if __name__ == "__main__":
    main()
