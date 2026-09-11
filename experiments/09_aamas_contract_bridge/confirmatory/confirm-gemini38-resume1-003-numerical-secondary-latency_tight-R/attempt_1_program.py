import numpy as np


def main():
    # Load the vectors
    X = np.load("vectors_secondary.npy")

    # Cast to float64 for high numerical precision during matrix multiplication
    X_64 = X.astype(np.float64)

    # Compute squared norms for each row
    sq_norms = np.sum(X_64**2, axis=1)

    # Compute Gram matrix G = X @ X.T using BLAS
    G = X_64 @ X_64.T

    # Pairwise squared Euclidean distances: ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2*(x_i . x_j)
    D2 = sq_norms[:, None] + sq_norms[None, :] - 2.0 * G

    # Exact zero on the diagonal
    np.fill_diagonal(D2, 0.0)

    # Clip any small negative numbers due to floating-point rounding
    np.maximum(D2, 0.0, out=D2)

    # Compute Euclidean distance matrix
    D = np.sqrt(D2)

    # Sum of Euclidean distances over all ordered pairs
    total = float(np.sum(D))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
