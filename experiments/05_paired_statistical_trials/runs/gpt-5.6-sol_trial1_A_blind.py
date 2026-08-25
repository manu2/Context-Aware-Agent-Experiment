#!/usr/bin/env python3

import math
import numpy as np

VECTOR_FILE = "vectors.npy"
EXPECTED_SHAPE = (8000, 1024)
BLOCK_SIZE = 512


def main() -> None:
    source = np.load(VECTOR_FILE, mmap_mode="r", allow_pickle=False)

    if source.shape != EXPECTED_SHAPE:
        raise ValueError(
            f"Expected shape {EXPECTED_SHAPE}, but found {source.shape}"
        )
    if source.dtype.kind != "f" or source.dtype.itemsize != 4:
        raise TypeError(f"Expected a float32 matrix, but found {source.dtype}")

    # Float64 reduces error in dot products, square roots, and accumulation.
    vectors = np.asarray(source, dtype=np.float64, order="C")
    squared_norms = np.einsum("ij,ij->i", vectors, vectors)

    n = vectors.shape[0]
    partial_sums = []

    # Compute only block pairs on and above the diagonal. Off-diagonal
    # blocks are doubled because the requested sum includes both (i, j)
    # and (j, i).
    for i0 in range(0, n, BLOCK_SIZE):
        i1 = min(i0 + BLOCK_SIZE, n)
        left = vectors[i0:i1]
        left_norms = squared_norms[i0:i1]

        for j0 in range(i0, n, BLOCK_SIZE):
            j1 = min(j0 + BLOCK_SIZE, n)
            right = vectors[j0:j1]

            # ||x-y||^2 = ||x||^2 + ||y||^2 - 2*x·y
            distances = left @ right.T
            distances *= -2.0
            distances += left_norms[:, None]
            distances += squared_norms[j0:j1][None, :]

            # Eliminate small negative values caused by floating-point error.
            np.maximum(distances, 0.0, out=distances)

            if i0 == j0:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))

            partial_sums.append(block_sum if i0 == j0 else 2.0 * block_sum)

    total = math.fsum(partial_sums)
    print(f"TOTAL_DIST:{total:.17g}")


if __name__ == "__main__":
    main()