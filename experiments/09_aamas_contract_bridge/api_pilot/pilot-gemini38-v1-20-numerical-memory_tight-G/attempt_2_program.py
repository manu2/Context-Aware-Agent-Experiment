import numpy as np


def main():
    vectors = np.load("vectors.npy")
    X = vectors.astype(np.float64)
    del vectors

    N = X.shape[0]
    norms_sq = np.sum(X**2, axis=1)

    total = 0.0
    batch_size = 1000

    for i in range(0, N, batch_size):
        batch = X[i : i + batch_size]
        b_len = len(batch)

        dot = batch @ X.T
        dists_sq = norms_sq[i : i + b_len, None] + norms_sq[None, :]
        dists_sq -= 2.0 * dot

        # Exactly zero out the diagonal
        dists_sq[np.arange(b_len), i + np.arange(b_len)] = 0.0

        np.maximum(dists_sq, 0.0, out=dists_sq)
        np.sqrt(dists_sq, out=dists_sq)

        total += float(dists_sq.sum())

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
