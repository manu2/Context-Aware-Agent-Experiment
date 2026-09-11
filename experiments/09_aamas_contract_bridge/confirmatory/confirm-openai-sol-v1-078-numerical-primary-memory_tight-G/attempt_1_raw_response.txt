import numpy as np


def main() -> None:
    vectors = np.load("vectors.npy", allow_pickle=False)
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    block_size = 1024
    count = vectors.shape[0]
    total = 0.0

    for i in range(0, count, block_size):
        i_end = min(i + block_size, count)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end]

        for j in range(i, count, block_size):
            j_end = min(j + block_size, count)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= -2.0
            distances += left_norms[:, None]
            distances += norms[j:j_end][None, :]
            np.maximum(distances, 0.0, out=distances)
            np.sqrt(distances, out=distances)

            if i == j:
                np.fill_diagonal(distances, 0.0)
                total += float(np.sum(distances, dtype=np.float64))
            else:
                total += 2.0 * float(np.sum(distances, dtype=np.float64))

    print("TOTAL:" + repr(total))


if __name__ == "__main__":
    main()
