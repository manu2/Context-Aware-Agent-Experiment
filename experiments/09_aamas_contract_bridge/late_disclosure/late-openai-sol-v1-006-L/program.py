import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np

x = np.load("vectors_secondary.npy")
norms = np.einsum("ij,ij->i", x, x, dtype=np.float32, optimize=True)

n = x.shape[0]
block_size = 512
total = 0.0

for start in range(0, n, block_size):
    stop = min(start + block_size, n)
    rows = stop - start

    distances = x[start:stop] @ x[start:].T
    distances *= np.float32(-2.0)
    distances += norms[start:stop, None]
    distances += norms[start:][None, :]
    np.maximum(distances, np.float32(0.0), out=distances)
    np.sqrt(distances, out=distances)

    diagonal = np.arange(rows)
    distances[diagonal, diagonal] = np.float32(0.0)

    stripe_sum = distances.sum(dtype=np.float64)
    within_block_sum = distances[:, :rows].sum(dtype=np.float64)
    total += float(2.0 * stripe_sum - within_block_sum)

print("TOTAL:" + format(total, ".17g"))
