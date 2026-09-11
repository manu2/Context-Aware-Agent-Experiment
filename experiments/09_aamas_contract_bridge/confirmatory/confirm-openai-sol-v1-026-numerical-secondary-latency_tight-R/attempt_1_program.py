import math
import numpy as np

x = np.asarray(np.load("vectors_secondary.npy", mmap_mode="r"), dtype=np.float64)
norms = np.einsum("ij,ij->i", x, x, optimize=True)

block_size = 512
n = x.shape[0]
partials = []

for i in range(0, n, block_size):
    i_end = min(i + block_size, n)
    xi = x[i:i_end]
    ni = norms[i:i_end]

    for j in range(i, n, block_size):
        j_end = min(j + block_size, n)
        xj = x[j:j_end]
        nj = norms[j:j_end]

        squared = xi @ xj.T
        squared *= -2.0
        squared += ni[:, None]
        squared += nj[None, :]
        np.maximum(squared, 0.0, out=squared)
        np.sqrt(squared, out=squared)

        if i == j:
            np.fill_diagonal(squared, 0.0)
            partials.append(float(np.sum(squared, dtype=np.float64)))
        else:
            partials.append(2.0 * float(np.sum(squared, dtype=np.float64)))

total = math.fsum(partials)
print(f"TOTAL:{total}")
