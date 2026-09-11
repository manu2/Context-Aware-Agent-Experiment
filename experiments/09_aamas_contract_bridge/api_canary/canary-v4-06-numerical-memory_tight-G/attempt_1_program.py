import numpy as np


def main():
    X = np.load("vectors.npy").astype(np.float64)
    n_vectors = X.shape[0]

    sq_norms = np.sum(X**2, axis=1)

    total = 0.0
    batch_size = 1000

    for i in range(0, n_vectors, batch_size):
        end_i = min(i + batch_size, n_vectors)
        X_batch = X[i:end_i]

        d2 = (
            sq_norms[i:end_i, None]
            + sq_norms[None, :]
            - 2.0 * (X_batch @ X.T)
        )
        np.maximum(d2, 0.0, out=d2)

        for r in range(end_i - i):
            d2[r, i + r] = 0.0

        total += np.sum(np.sqrt(d2))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
