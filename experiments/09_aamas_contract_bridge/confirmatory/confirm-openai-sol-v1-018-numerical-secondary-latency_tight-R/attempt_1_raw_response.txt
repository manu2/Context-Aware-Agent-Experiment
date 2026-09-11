import numpy as np

def main():
    source = np.load("vectors_secondary.npy", mmap_mode="r")
    vectors = np.array(source, dtype=np.float64, order="C", copy=True)
    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float64, optimize=True
    )

    block_size = 1024
    row_count = vectors.shape[0]
    total = np.longdouble(0)

    for i in range(0, row_count, block_size):
        i_end = min(i + block_size, row_count)
        left = vectors[i:i_end]
        left_norms = squared_norms[i:i_end]

        for j in range(i, row_count, block_size):
            j_end = min(j + block_size, row_count)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= -2.0
            distances += left_norms[:, None]
            distances += squared_norms[j:j_end][None, :]

            if i == j:
                np.fill_diagonal(distances, 0.0)

            np.maximum(distances, 0.0, out=distances)
            np.sqrt(distances, out=distances)

            block_sum = np.sum(distances, dtype=np.longdouble)
            total += block_sum if i == j else 2 * block_sum

    value = np.format_float_positional(total, unique=True, trim="-")
    print(f"TOTAL:{value}")

if __name__ == "__main__":
    main()
