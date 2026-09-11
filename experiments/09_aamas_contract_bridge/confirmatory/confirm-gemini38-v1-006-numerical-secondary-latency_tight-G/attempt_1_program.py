import numpy as np


def main():
    # Load vectors and cast to float64 to ensure high numerical precision
    X = np.load("vectors_secondary.npy").astype(np.float64)

    # Compute squared norms of each vector: ||x_i||^2
    sq = np.sum(X**2, axis=1)

    # Compute Gram matrix G = X @ X^T (8000 x 8000)
    # ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * <x_i, x_j>
    D2 = X @ X.T
    del X  # Free memory

    # In-place transformation to squared Euclidean distances
    D2 *= -2.0
    D2 += sq[:, None]
    D2 += sq[None, :]
    del sq

    # Ensure diagonal is strictly zero and eliminate negative values from precision limits
    np.fill_diagonal(D2, 0.0)
    np.maximum(D2, 0.0, out=D2)

    # Compute Euclidean distances in-place
    np.sqrt(D2, out=D2)

    # Sum over all ordered pairs
    total = float(np.sum(D2, dtype=np.float64))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
