import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors_secondary.npy")
    N = X.shape[0]

    # Mean-centering reduces the magnitude of coordinates, preventing cancellation errors
    mean = np.mean(X, axis=0, dtype=np.float64)

    total_dist = 0.0
    B = 1000

    for i in range(0, N, B):
        A = X[i : i + B].astype(np.float64) - mean
        sq_A = np.sum(A * A, axis=1)

        for j in range(i, N, B):
            if j == i:
                B_mat = A
                sq_B = sq_A
            else:
                B_mat = X[j : j + B].astype(np.float64) - mean
                sq_B = np.sum(B_mat * B_mat, axis=1)

            # Compute squared Euclidean distances in-place
            G = A @ B_mat.T
            G *= -2.0
            G += sq_A[:, None]
            G += sq_B[None, :]

            np.maximum(G, 0.0, out=G)
            np.sqrt(G, out=G)

            if j == i:
                np.fill_diagonal(G, 0.0)
                total_dist += float(np.sum(G, dtype=np.float64))
            else:
                total_dist += 2.0 * float(np.sum(G, dtype=np.float64))

    print(f"TOTAL:{total_dist}")


if __name__ == "__main__":
    main()
