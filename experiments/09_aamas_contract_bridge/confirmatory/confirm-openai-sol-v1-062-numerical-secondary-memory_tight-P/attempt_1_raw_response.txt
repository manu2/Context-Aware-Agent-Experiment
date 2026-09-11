import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import math
import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy", mmap_mode="r", allow_pickle=False)
    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError("Unexpected input array")

    norms = np.einsum(
        "ij,ij->i",
        vectors,
        vectors,
        dtype=np.float32,
        optimize=True,
    )

    block_size = 512
    n = vectors.shape[0]
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            right = vectors[j:j_end]

            distances = np.matmul(left, right.T)
            np.multiply(distances, np.float32(-2.0), out=distances)
            np.add(distances, left_norms[:, None], out=distances)
            np.add(distances, norms[j:j_end][None, :], out=distances)
            np.maximum(distances, np.float32(0.0), out=distances)
            np.sqrt(distances, out=distances)

            if i == j:
                np.fill_diagonal(distances, np.float32(0.0))
                partial_sums.append(distances.sum(dtype=np.float64))
            else:
                partial_sums.append(
                    2.0 * distances.sum(dtype=np.float64)
                )

    total = math.fsum(partial_sums)
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
