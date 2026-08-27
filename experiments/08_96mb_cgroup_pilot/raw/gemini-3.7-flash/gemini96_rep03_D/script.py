import numpy as np


def main():
    # Memory-map the input matrix to stay well within the 96 MB RAM limit
    vectors = np.load("vectors.npy", mmap_mode="r")
    n_vectors = vectors.shape[0]

    # Precompute squared L2 norms for all vectors using einsum to minimize memory allocation
    norms_sq = np.einsum("ij,ij->i", vectors, vectors)

    total_dist = 0.0
    block_size = 2000

    for i_start in range(0, n_vectors, block_size):
        i_end = min(i_start + block_size, n_vectors)
        block_i = vectors[i_start:i_end]
        norms_i = norms_sq[i_start:i_end]

        for j_start in range(i_start, n_vectors, block_size):
            j_end = min(j_start + block_size, n_vectors)
            block_j = vectors[j_start:j_end]
            norms_j = norms_sq[j_start:j_end]

            # Compute squared distances via BLAS dot product: ||u - v||^2 = ||u||^2 + ||v||^2 - 2(u . v)
            dot = np.dot(block_i, block_j.T)
            sq_dists = norms_i[:, None] + norms_j[None, :] - 2.0 * dot

            if i_start == j_start:
                # Diagonal block: sum only upper-triangular entries (i < j)
                triu_idx = np.triu_indices(i_end - i_start, k=1)
                dists_sq_upper = np.maximum(sq_dists[triu_idx], 0.0)
                total_dist += 2.0 * np.sum(
                    np.sqrt(dists_sq_upper), dtype=np.float64
                )
            else:
                # Off-diagonal block: all pairs correspond to strictly distinct indices
                np.maximum(sq_dists, 0.0, out=sq_dists)
                np.sqrt(sq_dists, out=sq_dists)
                total_dist += 2.0 * np.sum(sq_dists, dtype=np.float64)

    print(f"TOTAL_DIST:{total_dist}")


if __name__ == "__main__":
    main()