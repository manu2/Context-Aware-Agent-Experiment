import numpy as np


def main():
    # Load vectors and cast to float64 for numerical precision
    X = np.load("vectors_secondary.npy")
    X = np.asarray(X, dtype=np.float64)

    N = X.shape[0]
    sq_norms = np.sum(X**2, axis=1)

    total_dist = 0.0
    chunk_size = 1000

    for start in range(0, N, chunk_size):
        end = min(start + chunk_size, N)
        X_chunk = X[start:end]

        # Compute dot products for the chunk: shape (end - start, N)
        dist_sq = X_chunk @ X.T
        dist_sq *= -2.0
        dist_sq += sq_norms[start:end, None]
        dist_sq += sq_norms[None, :]

        # Clamp numerical inaccuracies to zero and compute square root
        np.maximum(dist_sq, 0.0, out=dist_sq)
        np.sqrt(dist_sq, out=dist_sq)

        # Zero out the diagonal explicitly
        chunk_indices = np.arange(end - start)
        global_indices = np.arange(start, end)
        dist_sq[chunk_indices, global_indices] = 0.0

        total_dist += float(np.sum(dist_sq))

    print(f"TOTAL:{total_dist}")


if __name__ == "__main__":
    main()
