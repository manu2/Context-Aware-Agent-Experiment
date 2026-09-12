import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors_secondary.npy")

    # Center vectors to maximize numerical stability of ||a - b||^2 = ||a||^2 + ||b||^2 - 2<a,b>
    X -= np.mean(X, axis=0, keepdims=True)

    sq_norms = np.sum(X**2, axis=1)

    # Compute pairwise inner products using GEMM
    G = np.dot(X, X.T)

    # Transform in-place to squared Euclidean distances: ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2(x_i . x_j)
    G *= -2.0
    G += sq_norms[:, None]
    G += sq_norms[None, :]

    # Clamp precision artifacts and ensure exact zero diagonal
    np.maximum(G, 0.0, out=G)
    np.fill_diagonal(G, 0.0)

    # Compute Euclidean distance
    np.sqrt(G, out=G)

    total = float(np.sum(G, dtype=np.float64))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
