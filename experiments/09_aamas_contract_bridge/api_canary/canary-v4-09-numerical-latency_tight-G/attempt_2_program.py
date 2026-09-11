import numpy as np


def main():
    # Load input array and promote to float64 for numerical precision
    X = np.load("vectors.npy").astype(np.float64)

    # Compute row-wise squared Euclidean norms: shape (8000,)
    sq_norms = np.sum(X**2, axis=1)

    # Compute Gram matrix G = X @ X.T: shape (8000, 8000)
    # ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * <x_i, x_j>
    D2 = X @ X.T
    D2 *= -2.0
    D2 += sq_norms[:, None]
    D2 += sq_norms[None, :]

    # Clamp numerical inaccuracies: exact zeros on the diagonal and non-negative values
    np.fill_diagonal(D2, 0.0)
    np.maximum(D2, 0.0, out=D2)

    # Euclidean distance matrix
    np.sqrt(D2, out=D2)

    total = float(np.sum(D2))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
