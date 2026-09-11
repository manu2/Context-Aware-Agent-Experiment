import math
import numpy as np

def main():
    vectors = np.asarray(np.load("vectors_secondary.npy", mmap_mode="r"), dtype=np.float64)
    norms = np.einsum("ij,ij->i", vectors, vectors, optimize=True)

    n = vectors.shape[0]
    block_size = 400
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= -2.0
            distances += norms[i:i_end, None]
            distances += norms[None, j:j_end]
            np.maximum(distances, 0.0, out=distances)

            if i == j:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            subtotal = float(np.sum(distances, dtype=np.float64))

            if i != j:
                subtotal *= 2.0
            partial_sums.append(subtotal)

    total = math.fsum(partial_sums)
    print(f"TOTAL:{total:.17g}")

if __name__ == "__main__":
    main()
