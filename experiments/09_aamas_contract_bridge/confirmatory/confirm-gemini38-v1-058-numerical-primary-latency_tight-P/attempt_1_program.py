import numpy as np


def main():
    vectors = np.load("vectors.npy")

    # Compute squared L2 norms of each row
    sq_norms = np.sum(vectors**2, axis=1)

    # Compute Gram matrix G = X @ X.T
    dist_sq = vectors @ vectors.T
    dist_sq *= -2.0
    dist_sq += sq_norms[:, None]
    dist_sq += sq_norms[None, :]

    # Clamp any negative values caused by numerical precision and set diagonal to 0
    np.maximum(dist_sq, 0.0, out=dist_sq)
    np.fill_diagonal(dist_sq, 0.0)

    # Compute Euclidean distances and sum over all pairs
    np.sqrt(dist_sq, out=dist_sq)
    total = np.sum(dist_sq, dtype=np.float64)

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
