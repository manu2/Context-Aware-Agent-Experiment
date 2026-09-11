import numpy as np


def main():
    # Load the 8000 x 1024 float32 vector array
    vectors = np.load("vectors_secondary.npy")

    # Cast to float64 for full precision in norm calculations and BLAS operations
    X = vectors.astype(np.float64)
    sq_norms = np.sum(X**2, axis=1)

    total = 0.0
    N = len(X)
    B = 1000

    for i in range(0, N, B):
        X_i = X[i : i + B]
        sq_i = sq_norms[i : i + B]
        for j in range(i, N, B):
            X_j = X[j : j + B]
            sq_j = sq_norms[j : j + B]

            # Compute block dot products: (B, 1024) @ (1024, B) -> (B, B)
            G = X_i @ X_j.T

            # ||x - y||^2 = ||x||^2 + ||y||^2 - 2(x . y)
            dist_sq = sq_i[:, None] + sq_j[None, :] - 2.0 * G
            np.maximum(dist_sq, 0.0, out=dist_sq)

            if i == j:
                np.fill_diagonal(dist_sq, 0.0)
                dists = np.sqrt(dist_sq)
                total += dists.sum()
            else:
                dists = np.sqrt(dist_sq)
                # By symmetry, ordered pairs (u, v) and (v, u) have equal distance
                total += 2.0 * dists.sum()

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
