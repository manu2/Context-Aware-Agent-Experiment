import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors_secondary.npy")
    N = X.shape[0]
    sq = np.einsum("ij,ij->i", X, X)

    B = 1000
    G = np.empty((B, B), dtype=np.float32)
    total = 0.0

    for i in range(0, N, B):
        X_i = X[i : i + B]
        sq_i = sq[i : i + B, None]
        for j in range(i, N, B):
            X_j = X[j : j + B]
            sq_j = sq[j : j + B]

            np.dot(X_i, X_j.T, out=G)
            G *= -2.0
            G += sq_i
            G += sq_j
            if i == j:
                np.fill_diagonal(G, 0.0)
            np.maximum(G, 0.0, out=G)
            np.sqrt(G, out=G)

            s = float(np.sum(G, dtype=np.float64))
            if i == j:
                total += s
            else:
                total += 2.0 * s

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
