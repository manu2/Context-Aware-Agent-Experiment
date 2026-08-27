import numpy as np


def main():
    # Load vector data (8000 x 1024, float32)
    vectors = np.load("vectors.npy")

    # Cast to float64 to ensure high numerical precision during distance computation
    X = vectors.astype(np.float64)
    n = X.shape[0]

    # Precompute squared L2 norms for each row: ||v_i||^2
    sq_norms = np.sum(X**2, axis=1)

    total_dist = 0.0
    chunk_size = 1000

    # Process in chunks to maintain low peak memory usage
    for i in range(0, n, chunk_size):
        X_chunk = X[i : i + chunk_size]
        sq_norms_chunk = sq_norms[i : i + chunk_size]

        # Compute squared Euclidean distance matrix block:
        # ||u - v||^2 = ||u||^2 + ||v||^2 - 2 * (u . v)
        gram_chunk = X_chunk @ X.T
        dist_sq = sq_norms_chunk[:, None] + sq_norms[None, :] - 2.0 * gram_chunk

        # Numerical stability: clamp small negative values to 0
        np.maximum(dist_sq, 0.0, out=dist_sq)

        # Compute Euclidean distances and accumulate sum
        total_dist += np.sum(np.sqrt(dist_sq))

    print(f"TOTAL_DIST:{total_dist}")


if __name__ == "__main__":
    main()