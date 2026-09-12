import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    x = np.load("vectors_secondary.npy", allow_pickle=False)
    n = x.shape[0]
    block_size = 256
    norms = np.empty(n, dtype=np.float32)
    total = 0.0

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        xb = x[start:end]

        distances = xb @ xb.T
        block_norms = np.diagonal(distances).copy()
        norms[start:end] = block_norms

        distances *= np.float32(-2.0)
        distances += block_norms[:, None]
        distances += block_norms[None, :]
        np.maximum(distances, np.float32(0.0), out=distances)
        np.fill_diagonal(distances, np.float32(0.0))
        np.sqrt(distances, out=distances)
        total += float(np.sum(distances, dtype=np.float64))

        if start:
            distances = xb @ x[:start].T
            distances *= np.float32(-2.0)
            distances += block_norms[:, None]
            distances += norms[:start][None, :]
            np.maximum(distances, np.float32(0.0), out=distances)
            np.sqrt(distances, out=distances)
            total += 2.0 * float(np.sum(distances, dtype=np.float64))

    print("TOTAL:" + format(total, ".17g"))


if __name__ == "__main__":
    main()
