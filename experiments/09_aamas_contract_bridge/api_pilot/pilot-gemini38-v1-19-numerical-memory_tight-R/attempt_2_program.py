import numpy as np


def main():
    vectors = np.load("vectors.npy")
    X = vectors.astype(np.float64)

    sq_norms = np.sum(X**2, axis=1)
    n = X.shape[0]

    total_dist = 0.0
    chunk_size = 1000

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        X_chunk = X[start:end]

        gram = np.dot(X_chunk, X.T)
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * gram
        np.maximum(d2, 0.0, out=d2)

        for i in range(start, end):
            d2[i - start, i] = 0.0

        d = np.sqrt(d2)
        total_dist += np.sum(d)

    print(f"TOTAL:{total_dist}")


if __name__ == "__main__":
    main()
