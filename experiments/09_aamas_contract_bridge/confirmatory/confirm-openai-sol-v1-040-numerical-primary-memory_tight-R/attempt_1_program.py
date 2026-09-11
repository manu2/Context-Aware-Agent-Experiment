import math
import numpy as np


def main():
    source = np.load("vectors.npy", mmap_mode="r")
    vectors = np.asarray(source, dtype=np.float64, order="C")
    norms = np.einsum("ij,ij->i", vectors, vectors)

    n = vectors.shape[0]
    block_size = 1024
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        a = vectors[i:i_end]
        a_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            b = vectors[j:j_end]

            distances = a @ b.T
            distances *= -2.0
            distances += a_norms[:, None]
            distances += norms[j:j_end][None, :]
            np.maximum(distances, 0.0, out=distances)
            np.sqrt(distances, out=distances)

            if i == j:
                upper = np.triu_indices(i_end - i, k=1)
                partial_sums.append(float(np.sum(distances[upper], dtype=np.float64)))
            else:
                partial_sums.append(float(np.sum(distances, dtype=np.float64)))

    total = 2.0 * math.fsum(partial_sums)
    print("TOTAL:" + repr(total))


if __name__ == "__main__":
    main()
