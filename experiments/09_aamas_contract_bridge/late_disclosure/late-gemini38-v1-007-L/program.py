import os

# Limit BLAS threads to 1 core to avoid context-switching overhead within CPU quota
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    filename = "vectors_secondary.npy"
    X = np.load(filename, mmap_mode="r")
    N, D = X.shape

    C = 1000  # Chunk size: keeps memory usage well under 128 MiB

    # Precompute squared norms in float64
    norms_sq = np.empty(N, dtype=np.float64)
    for start in range(0, N, C):
        end = min(start + C, N)
        chunk = X[start:end].astype(np.float64)
        norms_sq[start:end] = np.sum(chunk * chunk, axis=1)

    total_sum = 0.0
    num_blocks = (N + C - 1) // C

    for I in range(num_blocks):
        r1, r2 = I * C, min((I + 1) * C, N)
        X_I = X[r1:r2].astype(np.float64)
        n_I = norms_sq[r1:r2, None]

        # Diagonal block (I == J)
        G = np.dot(X_I, X_I.T)
        G *= -2.0
        G += n_I
        G += n_I.T
        np.fill_diagonal(G, 0.0)
        np.maximum(G, 0.0, out=G)
        np.sqrt(G, out=G)
        total_sum += np.sum(G)
        del G

        # Off-diagonal blocks (I < J)
        for J in range(I + 1, num_blocks):
            c1, c2 = J * C, min((J + 1) * C, N)
            X_J = X[c1:c2].astype(np.float64)
            n_J = norms_sq[None, c1:c2]

            G = np.dot(X_I, X_J.T)
            G *= -2.0
            G += n_I
            G += n_J
            np.maximum(G, 0.0, out=G)
            np.sqrt(G, out=G)
            # Count both (i, j) and (j, i) pairs
            total_sum += 2.0 * np.sum(G)
            del G

    print(f"TOTAL:{total_sum}")


if __name__ == "__main__":
    main()
