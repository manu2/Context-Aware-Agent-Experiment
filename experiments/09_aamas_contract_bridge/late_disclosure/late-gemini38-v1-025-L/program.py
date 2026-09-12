import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors.npy")
    N = X.shape[0]
    B = 1000

    norms_sq = np.empty((N, 1), dtype=np.float64)
    for i in range(0, N, B):
        norms_sq[i : i + B] = np.sum(
            X[i : i + B].astype(np.float64) ** 2, axis=1, keepdims=True
        )

    total = 0.0

    for i_start in range(0, N, B):
        i_end = min(i_start + B, N)
        Xi = X[i_start:i_end]
        norm_i = norms_sq[i_start:i_end]

        for j_start in range(i_start, N, B):
            j_end = min(j_start + B, N)
            Xj = X[j_start:j_end]
            norm_j = norms_sq[j_start:j_end]

            G = Xi @ Xj.T
            d_sq = norm_i + norm_j.T - 2.0 * G
            np.maximum(d_sq, 0.0, out=d_sq)
            d = np.sqrt(d_sq, out=d_sq)

            if i_start == j_start:
                triu_idx = np.triu_indices(i_end - i_start, k=1)
                total += 2.0 * float(np.sum(d[triu_idx], dtype=np.float64))
            else:
                total += 2.0 * float(np.sum(d, dtype=np.float64))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
