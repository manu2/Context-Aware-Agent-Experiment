import numpy as np


def main():
    # Load vectors and convert to float64 for numerical precision
    vectors = np.load("vectors.npy")
    X = vectors.astype(np.float64)
    del vectors

    n_rows = X.shape[0]
    norms_sq = np.sum(X * X, axis=1)

    total_distance = 0.0
    batch_size = 1000

    for start in range(0, n_rows, batch_size):
        end = min(start + batch_size, n_rows)

        # Compute dot products between current batch and all vectors: shape (end - start, n_rows)
        d_sq = X[start:end] @ X.T
        d_sq *= -2.0
        d_sq += norms_sq[start:end, None]
        d_sq += norms_sq[None, :]

        # Set exact zero along the diagonal
        for i in range(start, end):
            d_sq[i - start, i] = 0.0

        np.maximum(d_sq, 0.0, out=d_sq)
        np.sqrt(d_sq, out=d_sq)

        total_distance += float(np.sum(d_sq))

    print(f"TOTAL:{total_distance}")


if __name__ == "__main__":
    main()
