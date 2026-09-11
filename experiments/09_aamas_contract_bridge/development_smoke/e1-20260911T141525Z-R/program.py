import math
import numpy as np

def main():
    source = np.load("vectors.npy", mmap_mode="r")
    vectors = np.asarray(source, dtype=np.float64)
    norms = np.einsum("ij,ij->i", vectors, vectors)
    block_size = 256
    partials = []

    for i in range(0, vectors.shape[0], block_size):
        i_end = min(i + block_size, vectors.shape[0])
        left = vectors[i:i_end]

        for j in range(i, vectors.shape[0], block_size):
            j_end = min(j + block_size, vectors.shape[0])
            right = vectors[j:j_end]

            squared = (
                norms[i:i_end, None]
                + norms[None, j:j_end]
                - 2.0 * (left @ right.T)
            )
            np.maximum(squared, 0.0, out=squared)
            np.sqrt(squared, out=squared)

            if i == j:
                np.fill_diagonal(squared, 0.0)
                partials.append(float(np.sum(squared, dtype=np.float64)))
            else:
                partials.append(2.0 * float(np.sum(squared, dtype=np.float64)))

    total = math.fsum(partials)
    print(f"TOTAL:{total:.17f}")

if __name__ == "__main__":
    main()
