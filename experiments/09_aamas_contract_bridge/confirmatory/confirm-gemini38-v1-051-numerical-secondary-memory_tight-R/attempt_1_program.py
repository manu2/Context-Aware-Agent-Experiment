import numpy as np


def main():
    X = np.load("vectors_secondary.npy").astype(np.float64)

    # Compute squared L2 norm for each row
    norms_sq = np.sum(X**2, axis=1)

    # Compute Gram matrix: G = X @ X.T
    G = X @ X.T

    # Compute squared Euclidean distance matrix: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
    G *= -2.0
    G += norms_sq[:, None]
    G += norms_sq[None, :]

    # Numerical cleanup: clamp negatives to 0 and explicitly zero out the diagonal
    np.maximum(G, 0.0, out=G)
    np.fill_diagonal(G, 0.0)

    # Euclidean distance matrix
    np.sqrt(G, out=G)

    # Sum of distances over all ordered pairs
    total = float(np.sum(G))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
