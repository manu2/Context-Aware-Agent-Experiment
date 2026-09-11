import numpy as np


def main():
    # Load the vectors and convert to float64 for numerical precision
    X = np.load("vectors_secondary.npy").astype(np.float64)
    N = X.shape[0]

    # Precompute squared L2 norms for each vector: ||x_i||^2
    sq_norms = np.sum(X**2, axis=1)

    block_size = 1000
    total_upper = 0.0

    # Process block by block to minimize memory overhead
    for i in range(0, N, block_size):
        i_end = min(i + block_size, N)
        X_i = X[i:i_end]
        sq_i = sq_norms[i:i_end]

        # 1. Diagonal block: pairwise distances within X_i where a < b
        G_ii = X_i @ X_i.T
        D2_ii = sq_i[:, None] + sq_i[None, :] - 2.0 * G_ii
        np.maximum(D2_ii, 0.0, out=D2_ii)
        D_ii = np.sqrt(D2_ii)

        triu_idx = np.triu_indices(i_end - i, k=1)
        total_upper += float(np.sum(D_ii[triu_idx]))

        # 2. Off-diagonal blocks: distances between X_i and X_j (where all indices in i < j)
        for j in range(i_end, N, block_size):
            j_end = min(j + block_size, N)
            X_j = X[j:j_end]
            sq_j = sq_norms[j:j_end]

            G_ij = X_i @ X_j.T
            D2_ij = sq_i[:, None] + sq_j[None, :] - 2.0 * G_ij
            np.maximum(D2_ij, 0.0, out=D2_ij)
            D_ij = np.sqrt(D2_ij)

            total_upper += float(np.sum(D_ij))

    # Total over all ordered pairs (including zero diagonal):
    # sum_{i, j} d(x_i, x_j) = 2 * sum_{i < j} d(x_i, x_j)
    total = 2.0 * total_upper
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
