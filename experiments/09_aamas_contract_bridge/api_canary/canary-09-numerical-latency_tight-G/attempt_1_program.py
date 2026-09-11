import numpy as np


def main():
    # Load vectors (shape: 8000 x 1024, float32)
    vectors = np.load("vectors.npy")

    # Cast to float64 to ensure high numerical precision
    X = vectors.astype(np.float64)

    # Compute squared norms of each vector
    sq_norms = np.einsum("ij,ij->i", X, X)

    # Compute Gram matrix using optimized BLAS GEMM
    G = X @ X.T

    # Extract upper triangular indices (excluding diagonal since distance is 0)
    N = X.shape[0]
    i_idx, j_idx = np.triu_indices(N, k=1)

    # Compute squared Euclidean distances: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
    d2 = sq_norms[i_idx] + sq_norms[j_idx] - 2.0 * G[i_idx, j_idx]
    np.maximum(d2, 0.0, out=d2)
    np.sqrt(d2, out=d2)

    # Sum over all ordered pairs (symmetry gives 2 * sum of upper triangle)
    total = 2.0 * np.sum(d2, dtype=np.float64)

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
