import numpy as np


def main():
    vectors = np.load("vectors.npy")

    # Use float64 for numerical precision and center to minimize cancellation error
    X = vectors.astype(np.float64)
    X -= np.mean(X, axis=0)

    # Compute Gram matrix using high-performance BLAS GEMM
    G = X @ X.T

    # Squared norms
    sq = np.diag(G).copy()

    # D^2 = ||x_i||^2 + ||x_j||^2 - 2 <x_i, x_j>
    G *= -2.0
    G += sq[:, None]
    G += sq[None, :]

    # Ensure zero diagonal and clamp negative values caused by floating-point rounding
    np.fill_diagonal(G, 0.0)
    np.maximum(G, 0.0, out=G)

    # Compute Euclidean distances in-place
    np.sqrt(G, out=G)

    total = float(np.sum(G))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
