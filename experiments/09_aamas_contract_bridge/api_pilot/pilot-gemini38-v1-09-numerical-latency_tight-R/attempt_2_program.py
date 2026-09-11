import numpy as np


def main():
    vectors = np.load("vectors.npy")
    X = vectors.astype(np.float64)
    n = len(X)

    sq_norms = np.sum(X**2, axis=1)

    total = 0.0
    batch_size = 2000

    for i in range(0, n, batch_size):
        end = min(i + batch_size, n)
        X_batch = X[i:end]
        batch_len = end - i

        dots = X_batch @ X.T
        dists_sq = sq_norms[i:end, None] + sq_norms[None, :] - 2.0 * dots

        diag_rows = np.arange(batch_len)
        diag_cols = np.arange(i, end)
        dists_sq[diag_rows, diag_cols] = 0.0

        np.maximum(dists_sq, 0.0, out=dists_sq)
        dists = np.sqrt(dists_sq, out=dists_sq)
        total += float(dists.sum())

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
