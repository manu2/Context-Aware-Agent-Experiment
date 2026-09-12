import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import math
import numpy as np

vectors = np.load("vectors.npy", mmap_mode="r")
norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

n = vectors.shape[0]
block_size = 1024
partial_sums = []

for i in range(0, n, block_size):
    i_end = min(i + block_size, n)
    a = vectors[i:i_end]
    a_norms = norms[i:i_end]

    for j in range(i, n, block_size):
        j_end = min(j + block_size, n)
        b = vectors[j:j_end]

        distances = a @ b.T
        distances *= np.float32(-2.0)
        distances += a_norms[:, None]
        distances += norms[j:j_end][None, :]
        np.maximum(distances, np.float32(0.0), out=distances)
        np.sqrt(distances, out=distances)

        if i == j:
            np.fill_diagonal(distances, np.float32(0.0))
            partial_sums.append(float(np.sum(distances, dtype=np.float64)))
        else:
            partial_sums.append(
                2.0 * float(np.sum(distances, dtype=np.float64))
            )

total = math.fsum(partial_sums)
print("TOTAL:" + str(total))
