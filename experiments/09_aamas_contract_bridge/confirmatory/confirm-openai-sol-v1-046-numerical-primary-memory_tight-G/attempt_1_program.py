import math
import numpy as np


def main() -> None:
    vectors = np.load("vectors.npy", allow_pickle=False)
    norms = np.einsum(
        "ij,ij->i",
        vectors,
        vectors,
        dtype=np.float32,
        optimize=True,
    )

    block_size = 1024
    n = vectors.shape[0]
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            right = vectors[j:j_end]

            squared_distances = left @ right.T
            squared_distances *= -2.0
            squared_distances += left_norms[:, None]
            squared_distances += norms[j:j_end][None, :]
            np.maximum(squared_distances, 0.0, out=squared_distances)

            if i == j:
                np.fill_diagonal(squared_distances, 0.0)

            np.sqrt(squared_distances, out=squared_distances)
            block_sum = float(
                np.sum(squared_distances, dtype=np.float64)
            )

            partial_sums.append(block_sum if i == j else 2.0 * block_sum)

    total = math.fsum(partial_sums)
    print("TOTAL:" + repr(total))


if __name__ == "__main__":
    main()
