import math
import numpy as np


def main():
    source = np.load("vectors_secondary.npy", mmap_mode="r")
    vectors = np.array(source, dtype=np.float64, order="C", copy=True)
    del source

    n = vectors.shape[0]
    norms = np.einsum("ij,ij->i", vectors, vectors, optimize=True)
    block_size = 512
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        a = vectors[i:i_end]
        norm_a = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            b = vectors[j:j_end]

            distances = a @ b.T
            distances *= -2.0
            distances += norm_a[:, None]
            distances += norms[j:j_end][None, :]
            np.maximum(distances, 0.0, out=distances)

            if i == j:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))
            partial_sums.append(block_sum if i == j else 2.0 * block_sum)

    total = math.fsum(partial_sums)
    print("TOTAL:" + repr(total))


if __name__ == "__main__":
    main()
