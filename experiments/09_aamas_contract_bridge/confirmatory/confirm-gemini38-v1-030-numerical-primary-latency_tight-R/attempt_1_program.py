import numpy as np


def main():
    vectors = np.load("vectors.npy").astype(np.float64)
    sq_norms = np.sum(vectors**2, axis=1)

    # Compute Gram matrix: G = X @ X.T
    dists_sq = vectors @ vectors.T

    # Compute squared Euclidean distances in-place: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
    dists_sq *= -2.0
    dists_sq += sq_norms[:, None]
    dists_sq += sq_norms[None, :]

    np.maximum(dists_sq, 0.0, out=dists_sq)
    dists = np.sqrt(dists_sq, out=dists_sq)
    np.fill_diagonal(dists, 0.0)

    total = np.sum(dists)
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
