import numpy as np


def main() -> None:
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)
    norms = np.einsum("ij,ij->i", vectors, vectors, optimize=True)

    outer_size = 1024
    inner_size = 256
    row_count = vectors.shape[0]
    total = 0.0

    def block_sum(i0: int, i1: int, j0: int, j1: int, diagonal: bool) -> float:
        squared = vectors[i0:i1] @ vectors[j0:j1].T
        squared *= np.float32(-2.0)
        squared += norms[i0:i1, None]
        squared += norms[None, j0:j1]
        np.maximum(squared, np.float32(0.0), out=squared)

        if diagonal:
            np.fill_diagonal(squared, np.float32(0.0))

        np.sqrt(squared, out=squared)
        return float(np.sum(squared, dtype=np.float64))

    for outer_i in range(0, row_count, outer_size):
        outer_i_end = min(outer_i + outer_size, row_count)

        for outer_j in range(outer_i_end, row_count, outer_size):
            outer_j_end = min(outer_j + outer_size, row_count)
            total += 2.0 * block_sum(
                outer_i, outer_i_end, outer_j, outer_j_end, False
            )

        for i in range(outer_i, outer_i_end, inner_size):
            i_end = min(i + inner_size, outer_i_end)

            total += block_sum(i, i_end, i, i_end, True)

            for j in range(i_end, outer_i_end, inner_size):
                j_end = min(j + inner_size, outer_i_end)
                total += 2.0 * block_sum(i, i_end, j, j_end, False)

    print(f"TOTAL:{total:.17g}")


if __name__ == "__main__":
    main()
