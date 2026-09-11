import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np

x = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)
norms = np.einsum("ij,ij->i", x, x, optimize=True)
n = x.shape[0]
block = 1024
total = 0.0

for i in range(0, n, block):
    i_end = min(i + block, n)
    a = x[i:i_end]
    ni = norms[i:i_end]

    d = np.matmul(a, a.T)
    d *= -2.0
    d += ni[:, None]
    d += ni[None, :]
    np.maximum(d, 0.0, out=d)
    np.fill_diagonal(d, 0.0)
    np.sqrt(d, out=d)
    total += float(np.sum(d, dtype=np.float64))

    for j in range(0, i, block):
        j_end = min(j + block, n)
        b = x[j:j_end]
        d = np.matmul(a, b.T)
        d *= -2.0
        d += ni[:, None]
        d += norms[j:j_end][None, :]
        np.maximum(d, 0.0, out=d)
        np.sqrt(d, out=d)
        total += 2.0 * float(np.sum(d, dtype=np.float64))

print(f"TOTAL:{total}")
