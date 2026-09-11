import numpy as np


def main():
    # Load the vectors in float64 for maximum precision
    X = np.load("vectors_secondary.npy").astype(np.float64)

    # Compute pairwise squared Euclidean distances via Gram matrix:
    # ||u - v||^2 = ||u||^2 + ||v||^2 - 2 * <u, v>
    G = X @ X.T
    sq_norms = np.diag(G).copy()

    G *= -2.0
    G += sq_norms[:, None]
    G += sq_norms[None, :]

    # Clamp any small negative values due to floating-point imprecision to 0
    np.maximum(G, 0.0, out=G)
    np.fill_diagonal(G, 0.0)

    # Compute Euclidean distances
    np.sqrt(G, out=G)

    # Sum over all ordered pairs
    total = np.sum(G)

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
