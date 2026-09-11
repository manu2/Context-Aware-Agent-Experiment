import math
import numpy as np

vectors = np.load("vectors.npy", allow_pickle=False)
vectors = np.asarray(vectors, dtype=np.float64, order="C")

norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float64)
n = vectors.shape[0]
block_size = 512
partial_sums = []

for i in range(0, n, block_size):
    i_end = min(i + block_size, n)
    xi = vectors[i:i_end]
    ni = norms[i:i_end]

    for j in range(i, n, block_size):
        j_end = min(j + block_size, n)
        xj = vectors[j:j_end]
        nj = norms[j:j_end]

        distances = xi @ xj.T
        distances *= -2.0
        distances += ni[:, None]
        distances += nj[None, :]
        np.maximum(distances, 0.0, out=distances)

        if i == j:
            np.fill_diagonal(distances, 0.0)

        np.sqrt(distances, out=distances)
        block_sum = distances.sum(dtype=np.float64)
        partial_sums.append(block_sum if i == j else 2.0 * block_sum)

total = math.fsum(partial_sums)
print(f"TOTAL:{repr(total)}")
