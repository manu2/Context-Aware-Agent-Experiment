import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import math
import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy", mmap_mode="r", allow_pickle=False)
    n = vectors.shape[0]
    norms = np.einsum(
        "ij,ij->i",
        vectors,
        vectors,
        dtype=np.float32,
        optimize=False,
    )

    block_size = 512
    partials = []

    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        left = vectors[i0:i1]
        left_norms = norms[i0:i1]

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            right = vectors[j0:j1]

            distances = np.empty((i1 - i0, j1 - j0), dtype=np.float32)
            np.matmul(left, right.T, out=distances)

            np.multiply(distances, np.float32(-2.0), out=distances)
            np.add(distances, left_norms[:, None], out=distances)
            np.add(distances, norms[j0:j1][None, :], out=distances)
            np.maximum(distances, np.float32(0.0), out=distances)
            np.sqrt(distances, out=distances)

            if i0 == j0:
                np.fill_diagonal(distances, np.float32(0.0))
                partials.append(float(np.sum(distances, dtype=np.float64)))
            else:
                partials.append(
                    2.0 * float(np.sum(distances, dtype=np.float64))
                )

    total = math.fsum(partials)
    print("TOTAL:" + format(total, ".17g"))


if __name__ == "__main__":
    main()
