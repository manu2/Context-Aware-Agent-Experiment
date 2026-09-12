import os

# Constrain BLAS threading to 1 core to prevent thread contention within CPU quota
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    X = np.load("vectors_secondary.npy")
    n = X.shape[0]

    sq_norms = np.einsum("ij,ij->i", X, X)

    batch_size = 2000
    total_half = 0.0

    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        m = end - start

        # Compute dot products between current block and all rows from start to n
        g = np.dot(X[start:end], X[start:].T)

        d2 = sq_norms[start:end, None] + sq_norms[start:][None, :]
        d2 -= 2.0 * g
        np.maximum(d2, 0.0, out=d2)
        np.sqrt(d2, out=d2)

        # Strictly upper-triangular elements in the diagonal block
        diag_block = d2[:, :m]
        triu_i, triu_j = np.triu_indices(m, k=1)
        total_half += float(np.sum(diag_block[triu_i, triu_j], dtype=np.float64))

        # All elements in off-diagonal column blocks (j >= end > i)
        if d2.shape[1] > m:
            total_half += float(np.sum(d2[:, m:], dtype=np.float64))

    total = 2.0 * total_half
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
