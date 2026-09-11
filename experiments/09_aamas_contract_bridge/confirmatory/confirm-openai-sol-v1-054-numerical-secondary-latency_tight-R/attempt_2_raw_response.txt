import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy")
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    n = vectors.shape[0]
    block_size = 256
    total = 0.0

    for start in range(0, n, block_size):
        stop = min(start + block_size, n)
        size = stop - start

        distances = vectors[start:stop] @ vectors[start:].T
        distances *= -2.0
        distances += norms[start:stop, None]
        distances += norms[None, start:]
        np.maximum(distances, 0.0, out=distances)
        np.sqrt(distances, out=distances)

        lower_rows, lower_cols = np.tril_indices(size)
        distances[lower_rows, lower_cols] = 0.0

        total += float(np.sum(distances, dtype=np.float64))

    total *= 2.0
    print(f"TOTAL:{total!r}")


if __name__ == "__main__":
    main()
