import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy", allow_pickle=False)
    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError("Unexpected input array")

    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=True
    )

    total = 0.0
    block_size = 512
    row_count = vectors.shape[0]

    for i in range(0, row_count, block_size):
        i_end = min(i + block_size, row_count)
        left = vectors[i:i_end]
        left_norms = squared_norms[i:i_end, None]

        for j in range(i, row_count, block_size):
            j_end = min(j + block_size, row_count)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= np.float32(-2.0)
            distances += left_norms
            distances += squared_norms[j:j_end]
            np.maximum(distances, np.float32(0.0), out=distances)

            if i == j:
                np.fill_diagonal(distances, np.float32(0.0))

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))
            total += block_sum if i == j else 2.0 * block_sum

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
