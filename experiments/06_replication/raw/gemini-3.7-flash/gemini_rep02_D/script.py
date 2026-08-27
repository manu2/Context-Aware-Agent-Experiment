import numpy as np


def main():
    # Load vectors (8000 x 1024, float32 ~ 32.8 MB)
    vectors = np.load("vectors.npy")
    n = vectors.shape[0]

    # Precompute squared L2 norms for each row: ||v_i||^2
    # Computing along axis=1 in float64 for numerical precision
    sq_norms = np.sum(vectors.astype(np.float64) ** 2, axis=1)

    chunk_size = 1000
    total_upper_dist = 0.0

    # Process in blocks to stay well within 128 MB RAM and utilize fast BLAS sgemm
    for i_start in range(0, n, chunk_size):
        i_end = min(i_start + chunk_size, n)
        v_i = vectors[i_start:i_end]
        sq_i = sq_norms[i_start:i_end]

        for j_start in range(i_start, n, chunk_size):
            j_end = min(j_start + chunk_size, n)
            v_j = vectors[j_start:j_end]
            sq_j = sq_norms[j_start:j_end]

            # Fast matrix dot product: v_i @ v_j.T
            dot = np.dot(v_i, v_j.T, out=np.empty((i_end - i_start, j_end - j_start), dtype=np.float32))

            # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * (v_i . v_j)
            d_sq = sq_i[:, None] + sq_j[None, :] - 2.0 * dot
            np.maximum(d_sq, 0.0, out=d_sq)
            np.sqrt(d_sq, out=d_sq)

            if i_start == j_start:
                # Diagonal block: sum strictly upper triangular elements
                total_upper_dist += np.sum(np.triu(d_sq, k=1), dtype=np.float64)
            else:
                # Off-diagonal block: sum all elements
                total_upper_dist += np.sum(d_sq, dtype=np.float64)

    # Total sum over all pairs (i, j) is 2 * upper_triangular_sum since dist(i, i) = 0 and dist(i, j) = dist(j, i)
    total_dist = 2.0 * total_upper_dist
    print(f"TOTAL_DIST:{total_dist}")


if __name__ == "__main__":
    main()