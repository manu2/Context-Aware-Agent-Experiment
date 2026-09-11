import math
import numpy as np


def main() -> None:
    x = np.load("vectors_secondary.npy", mmap_mode="r")

    lo = np.min(x, axis=0).astype(np.float64)
    hi = np.max(x, axis=0).astype(np.float64)
    center = (lo + hi) * 0.5

    y = x.astype(np.float64)
    y -= center

    squared_norms = np.einsum("ij,ij->i", y, y, dtype=np.float64)
    n = y.shape[0]
    block_size = 512
    partial_sums = []

    for i in range(0, n, block_size):
        i_end = min(i + block_size, n)
        yi = y[i:i_end]
        ni = squared_norms[i:i_end]

        for j in range(i, n, block_size):
            j_end = min(j + block_size, n)
            yj = y[j:j_end]
            nj = squared_norms[j:j_end]

            distances = yi @ yj.T
            distances *= -2.0
            distances += ni[:, None]
            distances += nj[None, :]
            np.maximum(distances, 0.0, out=distances)

            if i == j:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))
            partial_sums.append(block_sum if i == j else 2.0 * block_sum)

    total = math.fsum(partial_sums)
    print(f"TOTAL:{total!r}")


if __name__ == "__main__":
    main()
