import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np

vectors = np.load("vectors.npy", allow_pickle=False)
n = vectors.shape[0]
block_size = 1000

norms = np.einsum("ij,ij->i", vectors, vectors, optimize=False)
work = np.empty((block_size, block_size), dtype=np.float32)

total = 0.0

for i in range(0, n, block_size):
    a = vectors[i:i + block_size]
    ni = norms[i:i + block_size]

    for j in range(i, n, block_size):
        b = vectors[j:j + block_size]
        nj = norms[j:j + block_size]

        np.matmul(a, b.T, out=work)
        work *= -2.0
        work += ni[:, None]
        work += nj[None, :]
        np.maximum(work, 0.0, out=work)

        if i == j:
            np.fill_diagonal(work, 0.0)

        np.sqrt(work, out=work)
        block_total = work.sum(dtype=np.float64)

        if i == j:
            total += block_total
        else:
            total += 2.0 * block_total

print("TOTAL:" + repr(float(total)))
