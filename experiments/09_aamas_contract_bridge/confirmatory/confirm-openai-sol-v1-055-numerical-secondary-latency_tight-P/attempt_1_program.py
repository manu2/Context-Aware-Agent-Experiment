import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy", allow_pickle=False)
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    n = vectors.shape[0]
    block_size = 256
    total = 0.0

    for start in range(0, n, block_size):
        stop = min(start + block_size, n)
        rows = vectors[start:stop]
        count = stop - start

        distances = rows @ vectors[start:].T
        distances *= -2.0
        distances += norms[start:stop, None]
        distances += norms[None, start:]
        np.maximum(distances, 0.0, out=distances)

        diagonal = np.arange(count)
        distances[diagonal, diagonal] = 0.0
        np.sqrt(distances, out=distances)

        total += distances[:, :count].sum(dtype=np.float64)
        total += 2.0 * distances[:, count:].sum(dtype=np.float64)

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
