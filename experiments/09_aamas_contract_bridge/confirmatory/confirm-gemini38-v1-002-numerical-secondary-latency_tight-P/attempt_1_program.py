import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors_secondary.npy")

    sq_norms = np.einsum("ij,ij->i", X, X)

    G = X @ X.T
    G *= -2.0
    G += sq_norms[:, None]
    G += sq_norms[None, :]

    np.maximum(G, 0.0, out=G)
    np.fill_diagonal(G, 0.0)
    np.sqrt(G, out=G)

    total = float(np.sum(G, dtype=np.float64))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
