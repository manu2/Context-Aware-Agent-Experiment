import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main() -> None:
    vectors = np.load("vectors_secondary.npy", allow_pickle=False)
    norms = np.sum(vectors * vectors, axis=1, dtype=np.float32)

    n = vectors.shape[0]
    block_size = 500
    work = np.empty((block_size, block_size), dtype=np.float32)
    total = 0.0

    for i in range(0, n, block_size):
        xi = vectors[i:i + block_size]
        ni = norms[i:i + block_size]
        bi = xi.shape[0]

        for j in range(i, n, block_size):
            xj = vectors[j:j + block_size]
            nj = norms[j:j + block_size]
            bj = xj.shape[0]
            distances = work[:bi, :bj]

            np.matmul(xi, xj.T, out=distances)
            distances *= -2.0
            distances += ni[:, None]
            distances += nj[None, :]
            np.maximum(distances, 0.0, out=distances)

            if i == j:
                distances.flat[::bj + 1] = 0.0

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))
            total += block_sum if i == j else 2.0 * block_sum

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
