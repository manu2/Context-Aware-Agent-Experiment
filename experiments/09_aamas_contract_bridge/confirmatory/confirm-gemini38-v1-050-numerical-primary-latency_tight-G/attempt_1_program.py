import numpy as np


def main():
    vectors = np.load("vectors.npy")
    X = vectors.astype(np.float64)
    N = X.shape[0]

    sq_norms = np.sum(X**2, axis=1)

    total = 0.0
    chunk_size = 2000

    for i in range(0, N, chunk_size):
        chunk = X[i : i + chunk_size]
        # Compute squared Euclidean distances: ||u||^2 + ||v||^2 - 2 <u, v>
        dists_sq = (
            sq_norms[i : i + chunk_size, None]
            + sq_norms[None, :]
            - 2.0 * (chunk @ X.T)
        )
        np.maximum(dists_sq, 0.0, out=dists_sq)
        dists = np.sqrt(dists_sq)

        # Ensure diagonal elements are strictly zero
        for r in range(len(chunk)):
            dists[r, i + r] = 0.0

        total += np.sum(dists)

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
