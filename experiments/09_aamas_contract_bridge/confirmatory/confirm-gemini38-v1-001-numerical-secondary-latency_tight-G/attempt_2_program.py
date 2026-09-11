import numpy as np


def main():
    # Load vectors (8000 x 1024, float32)
    vectors = np.load("vectors_secondary.npy")

    # Upcast to float64 for numerical precision
    X = vectors.astype(np.float64)

    # Compute squared norms for each vector: shape (8000,)
    norms = np.sum(X**2, axis=1)

    # Compute Gram matrix G = X @ X.T using optimized BLAS dgemm
    G = X @ X.T

    # Compute pairwise squared distance: ||u - v||^2 = ||u||^2 + ||v||^2 - 2 * (u . v)
    # Perform in-place operations on G to conserve memory
    G *= -2.0
    G += norms[:, None]
    G += norms[None, :]

    # Clean numerical inaccuracies and guarantee zero diagonal
    np.fill_diagonal(G, 0.0)
    np.maximum(G, 0.0, out=G)

    # Compute Euclidean distance
    np.sqrt(G, out=G)

    total = float(np.sum(G))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
