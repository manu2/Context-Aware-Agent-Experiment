import math
import numpy as np


def main() -> None:
    vectors = np.load("vectors_secondary.npy", allow_pickle=False)
    norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=True
    )

    n = vectors.shape[0]
    block_size = 512
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        left = vectors[i:i_end]
        left_norms = norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            right = vectors[j:j_end]

            distances = left @ right.T
            distances *= np.float32(-2.0)
            distances += left_norms[:, None]
            distances += norms[j:j_end][None, :]
            np.maximum(distances, np.float32(0.0), out=distances)
            np.sqrt(distances, out=distances)

            if i == j:
                np.fill_diagonal(distances, np.float32(0.0))
                partial_sums.append(
                    float(np.sum(distances, dtype=np.float64))
                )
            else:
                partial_sums.append(
                    2.0 * float(np.sum(distances, dtype=np.float64))
                )

    total = math.fsum(partial_sums)
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
