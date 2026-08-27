import numpy as np


def main():
    # Load vector data (8000 x 1024 float32, ~32.8 MB)
    vectors = np.load("vectors.npy")
    n_vectors = vectors.shape[0]

    # Precompute squared L2 norms for each vector (shape: (8000,))
    norms_sq = np.sum(vectors**2, axis=1)

    total_dist = 0.0
    block_size = 1000

    # Process pairwise distances in blocks to strictly adhere to the 128 MB RAM limit
    # Distance formula: ||u - v||^2 = ||u||^2 + ||v||^2 - 2 * (u . v)
    for i in range(0, n_vectors, block_size):
        i_end = min(i + block_size, n_vectors)
        v_i = vectors[i:i_end]
        n_i = norms_sq[i:i_end, None]

        # 1. Intra-block distances (within v_i)
        dot_intra = v_i @ v_i.T
        d2_intra = n_i + n_i.T - 2.0 * dot_intra
        np.maximum(d2_intra, 0.0, out=d2_intra)
        d_intra = np.sqrt(d2_intra)

        # Sum strictly upper triangle and double for symmetry (i != j)
        total_dist += 2.0 * float(np.sum(np.triu(d_intra, k=1)))

        # 2. Inter-block distances (between v_i and v_j for j > i)
        for j in range(i_end, n_vectors, block_size):
            j_end = min(j + block_size, n_vectors)
            v_j = vectors[j:j_end]
            n_j = norms_sq[j:j_end]

            dot_inter = v_i @ v_j.T
            d2_inter = n_i + n_j - 2.0 * dot_inter
            np.maximum(d2_inter, 0.0, out=d2_inter)
            d_inter = np.sqrt(d2_inter)

            # Multiply by 2.0 to account for both (i, j) and (j, i) pairs
            total_dist += 2.0 * float(np.sum(d_inter))

    print(f"TOTAL_DIST:{total_dist}")


if __name__ == "__main__":
    main()