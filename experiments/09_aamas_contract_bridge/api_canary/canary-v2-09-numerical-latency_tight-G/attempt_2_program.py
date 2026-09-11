import numpy as np


def main():
    # Load vectors as float64 for high numerical stability
    vectors = np.load("vectors.npy").astype(np.float64)
    n = vectors.shape[0]

    # Precompute squared norms of all vectors
    sq_norms = np.sum(vectors**2, axis=1)

    total_distance = 0.0
    batch_size = 1000

    for i in range(0, n, batch_size):
        batch = vectors[i : i + batch_size]
        batch_sq_norms = sq_norms[i : i + batch_size]

        # Compute squared Euclidean distance matrix for batch against all vectors
        # ||u - v||^2 = ||u||^2 + ||v||^2 - 2 * <u, v>
        gram = np.dot(batch, vectors.T)
        dist_sq = batch_sq_norms[:, None] + sq_norms[None, :] - 2.0 * gram

        # Clip negative values due to floating-point imprecision
        np.maximum(dist_sq, 0.0, out=dist_sq)
        dist = np.sqrt(dist_sq, out=dist_sq)

        total_distance += np.sum(dist)

    print(f"TOTAL:{total_distance:.10f}")


if __name__ == "__main__":
    main()
