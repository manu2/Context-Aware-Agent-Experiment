import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors_secondary.npy")

    # Compute squared Euclidean norms of each row
    norms = np.sum(X * X, axis=1)

    # Compute Gram matrix G = X @ X.T (float32, 8000x8000 -> 256 MB)
    G = X @ X.T

    # Compute pairwise squared Euclidean distances in-place:
    # ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * <x_i, x_j>
    G *= -2.0
    G += norms[:, None]
    G += norms[None, :]

    # Clamp negative values caused by floating-point rounding
    np.maximum(G, 0.0, out=G)

    # Compute Euclidean distances in-place
    np.sqrt(G, out=G)

    # Ensure zero diagonal
    np.fill_diagonal(G, 0.0)

    # Accumulate total in double precision
    total = float(np.sum(G, dtype=np.float64))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
