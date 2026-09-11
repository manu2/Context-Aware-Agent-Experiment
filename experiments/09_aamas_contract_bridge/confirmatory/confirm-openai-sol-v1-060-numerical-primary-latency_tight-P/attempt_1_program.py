import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    vectors = np.load("vectors.npy", allow_pickle=False)
    norms = np.sum(vectors * vectors, axis=1, dtype=np.float32)

    n = vectors.shape[0]
    block_size = 512
    total = 0.0

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= np.float32(-2.0)
            distances += left_norms[:, None]
            distances += norms[j:j_end][None, :]
            np.maximum(distances, np.float32(0.0), out=distances)
            np.sqrt(distances, out=distances)

            if i == j:
                np.fill_diagonal(distances, np.float32(0.0))
                total += float(np.sum(distances, dtype=np.float64))
            else:
                total += 2.0 * float(np.sum(distances, dtype=np.float64))

    print(f"TOTAL:{total:.17g}")


if __name__ == "__main__":
    main()
