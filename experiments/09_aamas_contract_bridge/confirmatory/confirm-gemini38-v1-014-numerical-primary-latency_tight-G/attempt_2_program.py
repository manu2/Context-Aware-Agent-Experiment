import numpy as np

def main():
    # Load input vectors (8000 x 1024, float32)
    vectors = np.load("vectors.npy")

    # Cast to float64 for numerical precision
    X = np.ascontiguousarray(vectors, dtype=np.float64)
    del vectors

    # Squared norms of each vector
    sq_norms = np.sum(X * X, axis=1)

    # Compute Gram matrix G = X @ X.T via BLAS (8000 x 8000 float64 ~ 512 MB)
    G = X @ X.T
    del X

    # In-place distance matrix calculation: D^2 = ||x_i||^2 + ||x_j||^2 - 2 * (x_i . x_j)
    G *= -2.0
    G += sq_norms[:, None]
    G += sq_norms[None, :]
    del sq_norms

    # Clamp rounding noise to zero and take square root
    np.maximum(G, 0.0, out=G)
    np.sqrt(G, out=G)

    # Zero out diagonal elements explicitly
    np.fill_diagonal(G, 0.0)

    # Compute the total sum of all pairwise Euclidean distances
    total = float(np.sum(G))
    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
