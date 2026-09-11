import math
import numpy as np

vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)
n = vectors.shape[0]
block_size = 1024

norms = np.einsum(
    "ij,ij->i",
    vectors,
    vectors,
    dtype=np.float32,
    optimize=True,
)

partial_sums = []

for i in range(0, n, block_size):
    i_end = min(i + block_size, n)
    a = vectors[i:i_end]
    a_norms = norms[i:i_end]

    for j in range(i, n, block_size):
        j_end = min(j + block_size, n)
        b = vectors[j:j_end]

        distances = a @ b.T
        distances *= -2.0
        distances += a_norms[:, None]
        distances += norms[j:j_end][None, :]
        np.maximum(distances, 0.0, out=distances)

        if i == j:
            np.fill_diagonal(distances, 0.0)

        np.sqrt(distances, out=distances)
        block_sum = float(np.sum(distances, dtype=np.float64))
        partial_sums.append(block_sum if i == j else 2.0 * block_sum)

total = math.fsum(partial_sums)
print("TOTAL:" + format(total, ".17g"))
