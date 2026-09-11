import numpy as np


def main():
    vectors = np.ascontiguousarray(np.load("vectors.npy", allow_pickle=False))
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    block_size = 2048
    row_count = vectors.shape[0]
    total = 0.0

    for i0 in range(0, row_count, block_size):
        i1 = min(i0 + block_size, row_count)
        left = vectors[i0:i1]
        left_norms = norms[i0:i1]

        for j0 in range(i0, row_count, block_size):
            j1 = min(j0 + block_size, row_count)
            right = vectors[j0:j1]

            distances = left @ right.T
            distances *= -2.0
            distances += left_norms[:, None]
            distances += norms[j0:j1][None, :]
            np.maximum(distances, 0.0, out=distances)

            if i0 == j0:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_total = float(np.sum(distances, dtype=np.float64))
            total += block_total if i0 == j0 else 2.0 * block_total

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
