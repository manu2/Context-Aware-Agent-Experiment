import math
import numpy as np


def main():
    source = np.load("vectors.npy", mmap_mode="r")
    x = np.array(source, dtype=np.float64, copy=True)

    # Translation preserves all pairwise distances and improves numerical stability.
    origin = x[0].copy()
    x -= origin

    norms = np.einsum("ij,ij->i", x, x, dtype=np.float64)
    n = x.shape[0]
    block_size = 512
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        a = x[i:i_end]
        a_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            b = x[j:j_end]

            squared = a @ b.T
            squared *= -2.0
            squared += a_norms[:, None]
            squared += norms[j:j_end][None, :]
            np.maximum(squared, 0.0, out=squared)

            if i == j:
                np.fill_diagonal(squared, 0.0)

            np.sqrt(squared, out=squared)
            subtotal = float(np.sum(squared, dtype=np.float64))
            partial_sums.append(subtotal if i == j else 2.0 * subtotal)

    total = math.fsum(partial_sums)
    print("TOTAL:" + format(total, ".17g"))


if __name__ == "__main__":
    main()
