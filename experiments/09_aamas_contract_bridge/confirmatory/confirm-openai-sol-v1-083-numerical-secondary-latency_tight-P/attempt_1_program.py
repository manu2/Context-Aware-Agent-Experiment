import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import numpy as np

x = np.load("vectors_secondary.npy", allow_pickle=False)
norm_sq = np.einsum("ij,ij->i", x, x, dtype=np.float32, optimize=False)

n = x.shape[0]
block_size = 128
total = 0.0

for start in range(0, n, block_size):
    stop = min(start + block_size, n)
    rows = stop - start

    distances = x[start:stop] @ x[start:].T
    distances *= np.float32(-2.0)
    distances += norm_sq[start:stop, None]
    distances += norm_sq[None, start:]
    np.maximum(distances, np.float32(0.0), out=distances)

    diagonal = np.arange(rows)
    distances[diagonal, diagonal] = np.float32(0.0)
    np.sqrt(distances, out=distances)

    panel_sum = np.sum(distances, dtype=np.float64)
    internal_sum = np.sum(distances[:, :rows], dtype=np.float64)
    total += 2.0 * panel_sum - internal_sum

print("TOTAL:" + format(total, ".17g"))
