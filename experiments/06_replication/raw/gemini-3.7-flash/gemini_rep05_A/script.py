import numpy as np


def main():
    # Load vector data
    vectors = np.load("vectors.npy")

    # Convert to float64 for numerical precision during distance computation
    vectors = np.asarray(vectors, dtype=np.float64)
    n = vectors.shape[0]

    # Precompute squared norms for each vector: ||v_i||^2
    sq_norms = np.sum(vectors**2, axis=1)

    total_dist = 0.0
    chunk_size = 1000  # Process in chunks to maintain low memory footprint

    for i in range(0, n, chunk_size):
        end = min(i + chunk_size, n)
        v_chunk = vectors[i:end]
        sq_norms_chunk = sq_norms[i:end]

        # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * <v_i, v_j>
        dists_sq = (
            sq_norms_chunk[:, None]
            + sq_norms[None, :]
            - 2.0 * np.dot(v_chunk, vectors.T)
        )

        # Numerical safety: clip negative values resulting from precision errors
        np.maximum(dists_sq, 0.0, out=dists_sq)

        dists = np.sqrt(dists_sq)
        total_dist += np.sum(dists)

    print(f"TOTAL_DIST:{total_dist}")


if __name__ == "__main__":
    main()