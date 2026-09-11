import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import math
import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)
    n = vectors.shape[0]
    block_size = 500

    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=True
    )

    partials = []

    for i in range(0, n, block_size):
        a = vectors[i:i + block_size]
        na = squared_norms[i:i + a.shape[0]]

        for j in range(i, n, block_size):
            b = vectors[j:j + block_size]
            nb = squared_norms[j:j + b.shape[0]]

            distances = a @ b.T
            distances *= np.float32(-2.0)
            distances += na[:, None]
            distances += nb[None, :]
            np.maximum(distances, np.float32(0.0), out=distances)

            if i == j:
                np.fill_diagonal(distances, np.float32(0.0))

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))
            partials.append(block_sum if i == j else 2.0 * block_sum)

    total = math.fsum(partials)
    print(f"TOTAL:{total!r}")


if __name__ == "__main__":
    main()
