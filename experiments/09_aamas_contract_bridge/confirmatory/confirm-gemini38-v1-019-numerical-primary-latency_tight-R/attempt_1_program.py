import numpy as np


def main():
    # Load vectors and cast to float64 for numerical precision during accumulation
    X = np.load("vectors.npy").astype(np.float64)

    # Compute squared norms for each vector: ||x_i||^2
    sq_norms = np.sum(X**2, axis=1)

    # Compute Gram matrix: G_ij = x_i . x_j
    G = X @ X.T

    # ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * (x_i . x_j)
    # Perform in-place operations on G to minimize memory usage
    G *= -2.0
    G += sq_norms[:, None]
    G += sq_norms[None, :]

    # Clamp small negative numbers caused by floating-point inaccuracy to 0.0
    np.maximum(G, 0.0, out=G)

    # Ensure the diagonal distances are strictly zero
    np.fill_diagonal(G, 0.0)

    # Compute Euclidean distances in-place
    np.sqrt(G, out=G)

    total = float(G.sum())
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
