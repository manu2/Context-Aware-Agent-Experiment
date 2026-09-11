import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np

x = np.load("vectors_secondary.npy", mmap_mode="r")
norms = np.einsum("ij,ij->i", x, x, dtype=np.float32)

n = x.shape[0]
block = 1000
work = np.empty((block, block), dtype=np.float32)
total = 0.0

for i in range(0, n, block):
    a = x[i:i + block]
    ni = norms[i:i + block]

    for j in range(i, n, block):
        b = x[j:j + block]
        nj = norms[j:j + block]
        g = work[:a.shape[0], :b.shape[0]]

        np.matmul(a, b.T, out=g)
        g *= -2.0
        g += ni[:, None]
        g += nj[None, :]
        np.maximum(g, 0.0, out=g)

        if i == j:
            np.fill_diagonal(g, 0.0)

        np.sqrt(g, out=g)
        subtotal = float(np.sum(g, dtype=np.float64))
        total += subtotal if i == j else 2.0 * subtotal

print(f"TOTAL:{total}")
