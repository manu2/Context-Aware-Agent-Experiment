import numpy as np


def main():
    # Load vectors and convert to float64 for precision
    X = np.load("vectors.npy").astype(np.float64)

    # Compute squared norms: ||x_i||^2
    sq_norms = np.einsum("ij,ij->i", X, X)

    # Compute pairwise squared Euclidean distances: ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 (x_i . x_j)
    D_sq = np.dot(X, X.T)
    D_sq *= -2.0
    D_sq += sq_norms[:, None]
    D_sq += sq_norms[None, :]

    # Clean up numerical inaccuracies
    np.fill_diagonal(D_sq, 0.0)
    np.maximum(D_sq, 0.0, out=D_sq)

    # Take elementwise square root to obtain Euclidean distances
    np.sqrt(D_sq, out=D_sq)

    total = np.sum(D_sq)
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
