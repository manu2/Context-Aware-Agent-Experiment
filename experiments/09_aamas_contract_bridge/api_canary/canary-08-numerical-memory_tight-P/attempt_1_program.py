import numpy as np


def main():
    # Memory-map the array to avoid loading unnecessary duplicate memory
    vectors = np.load("vectors.npy", mmap_mode="r")
    n = vectors.shape[0]

    # Precompute squared norms in float64 for high numerical precision
    norms = np.sum(np.square(vectors, dtype=np.float64), axis=1)

    block_size = 1000
    total_distance = 0.0

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        v_i = np.asarray(vectors[i:i_end], dtype=np.float64)
        norm_i = norms[i:i_end, None]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            v_j = np.asarray(vectors[j:j_end], dtype=np.float64)
            norm_j = norms[None, j:j_end]

            # Fast Gram matrix computation using BLAS GEMM
            g = np.dot(v_i, v_j.T)

            # Compute squared Euclidean distances: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
            d2 = norm_i + norm_j - 2.0 * g
            np.maximum(d2, 0.0, out=d2)

            if i == j:
                np.fill_diagonal(d2, 0.0)
                d = np.sqrt(d2, out=d2)
                total_distance += np.sum(d)
            else:
                d = np.sqrt(d2, out=d2)
                total_distance += 2.0 * np.sum(d)

    print(f"TOTAL:{total_distance}")


if __name__ == "__main__":
    main()
