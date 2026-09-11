import math
import numpy as np

vectors = np.load("vectors.npy", mmap_mode="r")
x = np.array(vectors, dtype=np.float64, copy=True)

center = (np.min(x, axis=0) + np.max(x, axis=0)) * 0.5
x -= center

norms = np.einsum("ij,ij->i", x, x, dtype=np.float64)
n = x.shape[0]
block_size = 1000
partial_sums = []

for i in range(0, n, block_size):
    i_end = min(i + block_size, n)
    a = x[i:i_end]

    for j in range(i, n, block_size):
        j_end = min(j + block_size, n)
        b = x[j:j_end]

        distances = a @ b.T
        distances *= -2.0
        distances += norms[i:i_end, None]
        distances += norms[None, j:j_end]
        np.maximum(distances, 0.0, out=distances)

        if i == j:
            np.fill_diagonal(distances, 0.0)

        np.sqrt(distances, out=distances)
        block_sum = float(np.sum(distances, dtype=np.float64))
        partial_sums.append(block_sum if i == j else 2.0 * block_sum)

total = math.fsum(partial_sums)
print(f"TOTAL:{total:.17g}")
