import numpy as np


def main():
    # Load the vectors
    vectors = np.load("vectors.npy")

    # Cast to float64 for numerical precision
    v64 = vectors.astype(np.float64)
    n = len(v64)

    # Precompute squared norms for each vector
    sq_norms = np.sum(v64**2, axis=1)

    total_distance = 0.0
    chunk_size = 1000

    for i in range(0, n, chunk_size):
        chunk = v64[i : i + chunk_size]
        chunk_len = len(chunk)

        # Dot products between current chunk and all vectors: shape (chunk_len, n)
        dots = chunk @ v64.T

        # Pairwise squared Euclidean distance: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
        dist_sq = sq_norms[i : i + chunk_len, None] + sq_norms[None, :] - 2.0 * dots

        # Numerical cleanup: clip negative values and zero out the exact diagonal
        np.maximum(dist_sq, 0.0, out=dist_sq)
        dist_sq[np.arange(chunk_len), np.arange(i, i + chunk_len)] = 0.0

        total_distance += np.sum(np.sqrt(dist_sq))

    print(f"TOTAL:{total_distance}")


if __name__ == "__main__":
    main()
