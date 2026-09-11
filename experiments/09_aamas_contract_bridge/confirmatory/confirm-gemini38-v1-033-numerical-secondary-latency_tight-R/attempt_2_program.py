import numpy as np


def main():
    # Load array and promote to float64 for precision
    X = np.load("vectors_secondary.npy").astype(np.float64)

    # Compute squared L2 norms for each row
    sq_norms = np.sum(X**2, axis=1)

    # Compute Gram matrix using optimized BLAS DGEMM
    G = X @ X.T

    # Compute squared pairwise distances in-place: ||u - v||^2 = ||u||^2 + ||v||^2 - 2(u . v)
    G *= -2.0
    G += sq_norms[:, None]
    G += sq_norms[None, :]

    # Numerical safeguards
    np.maximum(G, 0.0, out=G)
    np.fill_diagonal(G, 0.0)

    # Element-wise square root to get Euclidean distances
    np.sqrt(G, out=G)

    # Sum across all ordered pairs
    total = float(np.sum(G))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
