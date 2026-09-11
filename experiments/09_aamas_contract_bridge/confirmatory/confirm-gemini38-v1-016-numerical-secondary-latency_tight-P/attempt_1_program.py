import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors_secondary.npy")

    sq = np.sum(X * X, axis=1)

    # Compute Gram matrix G = X @ X.T
    G = X @ X.T

    # Pairwise squared Euclidean distances: ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 <x_i, x_j>
    G *= -2.0
    G += sq[:, None]
    G += sq[None, :]

    # Clamp small negative numbers caused by floating-point inaccuracy
    np.maximum(G, 0.0, out=G)
    np.sqrt(G, out=G)
    np.fill_diagonal(G, 0.0)

    total = float(G.sum(dtype=np.float64))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
