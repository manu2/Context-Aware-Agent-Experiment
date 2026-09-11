import numpy as np


def main():
    # Load vectors and cast to float64 to maintain high numerical precision
    vectors = np.load("vectors_secondary.npy").astype(np.float64)
    n = vectors.shape[0]

    # Precompute squared norms for each vector
    sq_norms = np.sum(vectors**2, axis=1)

    block_size = 1000
    upper_sum = 0.0

    # Iterate over upper-triangular block pairs
    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        v_i = vectors[i:i_end]
        norms_i = sq_norms[i:i_end, None]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            v_j = vectors[j:j_end]
            norms_j = sq_norms[None, j:j_end]

            # Compute squared distances using BLAS matrix multiplication
            d2 = norms_i + norms_j - 2.0 * (v_i @ v_j.T)
            np.maximum(d2, 0.0, out=d2)
            np.sqrt(d2, out=d2)

            if i == j:
                # Diagonal block: only sum strictly upper-triangular entries (i < j)
                upper_sum += np.triu(d2, k=1).sum()
            else:
                # Off-diagonal block: every entry satisfies row_index < col_index
                upper_sum += d2.sum()

    # Total over all ordered pairs including the zero diagonal
    total = 2.0 * upper_sum
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
