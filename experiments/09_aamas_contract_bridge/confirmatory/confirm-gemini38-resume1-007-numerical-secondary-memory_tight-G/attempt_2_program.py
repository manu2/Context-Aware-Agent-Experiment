import numpy as np


def main():
    # Load data without modifying the source file
    X = np.load("vectors_secondary.npy").astype(np.float64)
    n = X.shape[0]

    # Precompute squared norms for each vector
    sq_norms = np.sum(X**2, axis=1)

    total_dist = 0.0
    chunk_size = 1000

    for i in range(0, n, chunk_size):
        chunk_len = min(chunk_size, n - i)
        X_chunk = X[i : i + chunk_len]

        # Dot product via BLAS GEMM: shape (chunk_len, n)
        G_chunk = X_chunk @ X.T

        # Pairwise squared distances: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
        d2 = sq_norms[i : i + chunk_len, None] + sq_norms[None, :] - 2.0 * G_chunk

        # Ensure diagonal elements are strictly zero
        for k in range(chunk_len):
            d2[k, i + k] = 0.0

        # Guard against small negative roundoff errors before square root
        np.maximum(d2, 0.0, out=d2)
        np.sqrt(d2, out=d2)

        total_dist += float(np.sum(d2))

    print(f"TOTAL:{total_dist}")


if __name__ == "__main__":
    main()
