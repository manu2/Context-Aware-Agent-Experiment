import math
import numpy as np

vectors = np.load("vectors_secondary.npy", allow_pickle=False).astype(np.float64, copy=False)
norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float64)

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

        distances = left @ right.T
        distances *= -2.0
        distances += left_norms[:, None]
        distances += norms[j:j_end][None, :]

        if i == j:
            np.fill_diagonal(distances, 0.0)

        np.maximum(distances, 0.0, out=distances)
        np.sqrt(distances, out=distances)

        block_sum = float(np.sum(distances, dtype=np.float64))
        partial_sums.append(block_sum if i == j else 2.0 * block_sum)

total = math.fsum(partial_sums)
print(f"TOTAL:{total}")
