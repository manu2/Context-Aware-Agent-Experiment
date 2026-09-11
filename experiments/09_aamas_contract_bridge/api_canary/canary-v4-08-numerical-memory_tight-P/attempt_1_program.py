import numpy as np


def main():
    # Load vector data
    X = np.load("vectors.npy", mmap_mode="r")
    N = X.shape[0]

    # Precompute squared L2 norms for each row
    sq_norms = np.einsum("ij,ij->i", X, X)

    total_upper = 0.0
    batch_size = 500

    for i in range(0, N, batch_size):
        i_end = min(i + batch_size, N)
        X_batch = X[i:i_end]
        sq_batch = sq_norms[i:i_end]
        M = i_end - i

        # 1. Intra-block pairwise distances (pairs where both indices are in [i, i_end))
        dot_intra = X_batch @ X_batch.T
        dot_intra *= -2.0
        dot_intra += sq_batch[:, None]
        dot_intra += sq_batch[None, :]
        np.maximum(dot_intra, 0.0, out=dot_intra)
        np.sqrt(dot_intra, out=dot_intra)

        r_idx, c_idx = np.triu_indices(M, k=1)
        total_upper += float(dot_intra[r_idx, c_idx].sum(dtype=np.float64))
        del dot_intra

        # 2. Inter-block pairwise distances (row a in [i, i_end), row b in [i_end, N))
        if i_end < N:
            dot_inter = X_batch @ X[i_end:].T
            dot_inter *= -2.0
            dot_inter += sq_batch[:, None]
            dot_inter += sq_norms[i_end:][None, :]
            np.maximum(dot_inter, 0.0, out=dot_inter)
            np.sqrt(dot_inter, out=dot_inter)

            total_upper += float(dot_inter.sum(dtype=np.float64))
            del dot_inter

    # Total over all ordered pairs (a, b) including diagonal (which has distance 0)
    total = 2.0 * total_upper
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
