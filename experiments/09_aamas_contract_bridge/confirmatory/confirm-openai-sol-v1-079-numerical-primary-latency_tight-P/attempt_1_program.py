import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    vectors = np.load("vectors.npy", allow_pickle=False)
    norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=False
    )

    n = vectors.shape[0]
    block_size = 512
    total = 0.0

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end, None]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            distances = left @ vectors[j:j_end].T
            distances *= -2.0
            distances += left_norms
            distances += norms[None, j:j_end]
            np.maximum(distances, 0.0, out=distances)

            if i == j:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_total = distances.sum(dtype=np.float64)
            total += block_total if i == j else 2.0 * block_total

    print(f"TOTAL:{total:.17g}")


if __name__ == "__main__":
    main()
