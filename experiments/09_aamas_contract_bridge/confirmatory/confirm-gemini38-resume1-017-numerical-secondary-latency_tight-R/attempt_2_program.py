import numpy as np


def main():
    # Load vectors and promote to float64 for numerical precision
    X = np.load("vectors_secondary.npy").astype(np.float64)

    # Compute squared L2 norms of each row
    norms = np.sum(X**2, axis=1)

    # Compute Gram matrix using optimized BLAS GEMM: G = X @ X.T
    G = X @ X.T

    # Compute pairwise squared Euclidean distances in place:
    # ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * <x_i, x_j>
    G *= -2.0
    G += norms[:, None]
    G += norms[None, :]

    # Clamp any slight negative numerical artifacts to 0.0 and take square root
    np.maximum(G, 0.0, out=G)
    np.sqrt(G, out=G)
    np.fill_diagonal(G, 0.0)

    total = float(np.sum(G))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
