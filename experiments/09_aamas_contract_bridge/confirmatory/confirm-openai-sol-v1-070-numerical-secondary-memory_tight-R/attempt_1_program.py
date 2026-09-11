import math
import numpy as np


def main():
    source = np.load("vectors_secondary.npy", mmap_mode="r", allow_pickle=False)
    vectors = np.asarray(source, dtype=np.float64, order="C")
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float64)

    block_size = 512
    block_totals = []
    row_count = vectors.shape[0]

    for i in range(0, row_count, block_size):
        i_end = min(i + block_size, row_count)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end]

        for j in range(i, row_count, block_size):
            j_end = min(j + block_size, row_count)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= -2.0
            distances += left_norms[:, None]
            distances += norms[j:j_end][None, :]
            np.maximum(distances, 0.0, out=distances)

            if i == j:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))
            block_totals.append(block_sum if i == j else 2.0 * block_sum)

    total = math.fsum(block_totals)
    print(f"TOTAL:{total:.17f}")


if __name__ == "__main__":
    main()
