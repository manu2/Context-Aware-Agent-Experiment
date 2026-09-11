import numpy as np


def main():
    # Load vectors and cast to float64 to ensure high numerical precision
    X = np.load("vectors.npy").astype(np.float64)

    # Compute squared Euclidean norms of each vector
    sq_norms = np.einsum("ij,ij->i", X, X)

    # Compute the Gram matrix G = X @ X.T
    G = X @ X.T

    # Compute pairwise squared Euclidean distances: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
    D2 = sq_norms[:, None] + sq_norms[None, :]
    D2 -= 2.0 * G
    del G

    # Numerical cleanup: prevent tiny negative values and ensure exact zero diagonal
    np.maximum(D2, 0.0, out=D2)
    np.fill_diagonal(D2, 0.0)

    # Compute Euclidean distances
    np.sqrt(D2, out=D2)

    total = D2.sum(dtype=np.float64)
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
