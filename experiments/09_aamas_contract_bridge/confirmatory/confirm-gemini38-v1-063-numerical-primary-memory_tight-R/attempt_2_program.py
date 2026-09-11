import numpy as np


def main():
    X = np.load("vectors.npy").astype(np.float64)
    sq_norms = np.sum(X**2, axis=1)

    # Compute Gram matrix G = X @ X.T
    G = X @ X.T

    # ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * <x_i, x_j>
    G *= -2.0
    G += sq_norms[:, None]
    G += sq_norms[None, :]

    np.fill_diagonal(G, 0.0)
    np.maximum(G, 0.0, out=G)
    np.sqrt(G, out=G)

    total = float(np.sum(G))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
