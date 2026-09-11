import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors.npy")

    # Compute Gram matrix G = X @ X.T
    G = X @ X.T

    # s_i = ||x_i||^2
    s = np.diag(G).copy()

    # ||x_i - x_j||^2 = s_i + s_j - 2 G_ij
    G *= -2.0
    G += s[:, None]
    G += s[None, :]

    # Clamp small negative values from floating point inaccuracies to 0
    np.maximum(G, 0.0, out=G)

    # Compute Euclidean distances
    np.sqrt(G, out=G)

    # Ensure zero diagonal
    np.fill_diagonal(G, 0.0)

    total = float(np.sum(G, dtype=np.float64))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
