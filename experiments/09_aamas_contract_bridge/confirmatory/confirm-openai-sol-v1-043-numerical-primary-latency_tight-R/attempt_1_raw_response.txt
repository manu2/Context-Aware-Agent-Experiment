import math
import numpy as np


def main():
    source = np.load("vectors.npy", mmap_mode="r")
    vectors = np.asarray(source, dtype=np.float64)

    n, dimensions = vectors.shape
    norms = np.einsum("ij,ij->i", vectors, vectors)
    block_size = 512
    tolerance_factor = 64.0 * np.finfo(np.float64).eps * dimensions
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        a = vectors[i:i_end]
        a_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            b = vectors[j:j_end]
            b_norms = norms[j:j_end]

            squared = a_norms[:, None] + b_norms[None, :]
            squared -= 2.0 * (a @ b.T)

            scale = a_norms[:, None] + b_norms[None, :]
            near_zero = squared <= tolerance_factor * scale

            if i == j:
                diagonal = np.arange(i_end - i)
                near_zero[diagonal, diagonal] = False
                squared[diagonal, diagonal] = 0.0

            rows, columns = np.nonzero(near_zero)
            for start in range(0, rows.size, 4096):
                r = rows[start:start + 4096]
                c = columns[start:start + 4096]
                differences = a[r] - b[c]
                squared[r, c] = np.einsum(
                    "ij,ij->i", differences, differences
                )

            np.maximum(squared, 0.0, out=squared)
            np.sqrt(squared, out=squared)

            block_sum = float(np.sum(squared, dtype=np.float64))
            partial_sums.append(block_sum if i == j else 2.0 * block_sum)

    total = math.fsum(partial_sums)
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
