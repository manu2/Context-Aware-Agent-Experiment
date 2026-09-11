import math
import numpy as np

vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)
x = np.asarray(vectors, dtype=np.float64)

row_norms = np.einsum("ij,ij->i", x, x, dtype=np.float64)
block_size = 512
n = x.shape[0]
partial_sums = []

for i in range(0, n, block_size):
    i_end = min(i + block_size, n)
    xi = x[i:i_end]
    ni = row_norms[i:i_end, None]

    for j in range(i, n, block_size):
        j_end = min(j + block_size, n)
        xj = x[j:j_end]

        squared = xi @ xj.T
        squared *= -2.0
        squared += ni
        squared += row_norms[None, j:j_end]
        np.maximum(squared, 0.0, out=squared)

        if i == j:
            np.fill_diagonal(squared, 0.0)

        np.sqrt(squared, out=squared)
        block_sum = float(np.sum(squared, dtype=np.float64))
        partial_sums.append(block_sum if i == j else 2.0 * block_sum)

total = math.fsum(partial_sums)
print(f"TOTAL:{total:.10f}")
