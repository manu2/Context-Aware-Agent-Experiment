import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import numpy as np

vectors = np.load("vectors.npy", mmap_mode="r")
n = vectors.shape[0]
block_size = 1000

norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)
work = np.empty((block_size, block_size), dtype=np.float32)
total = 0.0

for i in range(0, n, block_size):
    i_end = min(i + block_size, n)
    x = vectors[i:i_end]
    ni = norms[i:i_end]

    for j in range(i, n, block_size):
        j_end = min(j + block_size, n)
        y = vectors[j:j_end]
        nj = norms[j:j_end]
        out = work[:i_end - i, :j_end - j]

        np.matmul(x, y.T, out=out)
        out *= -2.0
        out += ni[:, None]
        out += nj[None, :]
        np.maximum(out, 0.0, out=out)
        np.sqrt(out, out=out)

        if i == j:
            np.fill_diagonal(out, 0.0)
            total += float(np.sum(out, dtype=np.float64))
        else:
            total += 2.0 * float(np.sum(out, dtype=np.float64))

print(f"TOTAL:{total}")
