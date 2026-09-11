import numpy as np

def main():
    vectors = np.load("vectors_secondary.npy")
    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError("Unexpected input array")

    vectors = np.ascontiguousarray(vectors)
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    block_size = 1024
    n = vectors.shape[0]
    total = np.float64(0.0)

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

            if i == j:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = np.sum(distances, dtype=np.float64)
            total += block_sum if i == j else 2.0 * block_sum

    print("TOTAL:" + str(float(total)))

if __name__ == "__main__":
    main()
