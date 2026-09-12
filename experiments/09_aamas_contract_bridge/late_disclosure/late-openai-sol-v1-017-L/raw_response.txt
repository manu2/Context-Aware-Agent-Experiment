import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy", mmap_mode="r", allow_pickle=False)
    norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=True
    )

    block_size = 512
    count = vectors.shape[0]
    total = 0.0

    for i in range(0, count, block_size):
        i_end = min(i + block_size, count)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end, None]

        for j in range(i, count, block_size):
            j_end = min(j + block_size, count)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= np.float32(-2.0)
            distances += left_norms
            distances += norms[j:j_end][None, :]
            np.maximum(distances, np.float32(0.0), out=distances)

            if i == j:
                np.fill_diagonal(distances, np.float32(0.0))

            np.sqrt(distances, out=distances)
            subtotal = float(np.sum(distances, dtype=np.float64))
            total += subtotal if i == j else 2.0 * subtotal

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
