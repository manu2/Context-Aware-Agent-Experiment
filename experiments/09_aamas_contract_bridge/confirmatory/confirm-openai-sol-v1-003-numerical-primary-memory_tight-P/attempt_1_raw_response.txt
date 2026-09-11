import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import math
import numpy as np


def main():
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)
    norms = np.einsum(
        "ij,ij->i",
        vectors,
        vectors,
        dtype=np.float32,
        optimize=False,
    )

    block_size = 1024
    n = vectors.shape[0]
    partials = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            right = vectors[j:j_end]
            right_norms = norms[j:j_end]

            distances = left @ right.T
            distances *= np.float32(-2.0)
            np.add(distances, left_norms[:, None], out=distances)
            np.add(distances, right_norms[None, :], out=distances)
            np.maximum(distances, np.float32(0.0), out=distances)

            if i == j:
                np.fill_diagonal(distances, np.float32(0.0))

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))

            partials.append(block_sum if i == j else 2.0 * block_sum)
            del distances

    total = math.fsum(partials)
    print("TOTAL:" + str(total))


if __name__ == "__main__":
    main()
