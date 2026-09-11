import math
import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy", allow_pickle=False)
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    n = vectors.shape[0]
    block_size = 512
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end]

        distances = left @ left.T
        distances *= -2.0
        distances += left_norms[:, None]
        distances += left_norms[None, :]
        np.maximum(distances, 0.0, out=distances)
        np.fill_diagonal(distances, 0.0)
        np.sqrt(distances, out=distances)
        partial_sums.append(float(np.sum(distances, dtype=np.float64)))

        for j in range(i_end, n, block_size):
            j_end = min(j + block_size, n)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= -2.0
            distances += left_norms[:, None]
            distances += norms[j:j_end][None, :]
            np.maximum(distances, 0.0, out=distances)
            np.sqrt(distances, out=distances)
            partial_sums.append(
                2.0 * float(np.sum(distances, dtype=np.float64))
            )

    print(f"TOTAL:{math.fsum(partial_sums)}")


if __name__ == "__main__":
    main()
