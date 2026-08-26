import numpy as np


def main():
    # Load vectors (8000 x 1024, float32)
    V = np.load('vectors.npy')
    n_samples = V.shape[0]

    # Precompute squared L2 norms for each vector
    sq_norms = np.sum(V ** 2, axis=1, dtype=np.float32)

    total_dist = 0.0
    batch_size = 1000

    # Process in batches to stay well below the 128 MB memory limit
    for i in range(0, n_samples, batch_size):
        end_i = min(i + batch_size, n_samples)
        V_batch = V[i:end_i]

        # Compute squared Euclidean distance using: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
        # Perform matrix multiplication and in-place arithmetic to minimize memory allocations
        dists = np.dot(V_batch, V.T)
        dists *= -2.0
        dists += sq_norms[i:end_i, np.newaxis]
        dists += sq_norms[np.newaxis, :]

        # Clamp numerical inaccuracies below zero and zero out diagonal
        np.maximum(dists, 0.0, out=dists)
        np.fill_diagonal(dists[:, i:end_i], 0.0)

        # Compute Euclidean distance
        np.sqrt(dists, out=dists)

        # Accumulate with float64 precision
        total_dist += float(np.sum(dists, dtype=np.float64))

    print(f"TOTAL_DIST:{total_dist}")


if __name__ == '__main__':
    main()