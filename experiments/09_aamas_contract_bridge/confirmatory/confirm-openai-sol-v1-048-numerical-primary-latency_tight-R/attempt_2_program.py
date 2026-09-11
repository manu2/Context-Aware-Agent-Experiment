import os

try:
    cpu_count = len(os.sched_getaffinity(0))
except AttributeError:
    cpu_count = os.cpu_count() or 1

threads = str(max(1, min(cpu_count, 8)))
os.environ["OPENBLAS_NUM_THREADS"] = threads
os.environ["OMP_NUM_THREADS"] = threads
os.environ["MKL_NUM_THREADS"] = threads
os.environ["VECLIB_MAXIMUM_THREADS"] = threads
os.environ["NUMEXPR_NUM_THREADS"] = threads

import numpy as np

vectors = np.load("vectors.npy", allow_pickle=False)
norms = np.sum(vectors * vectors, axis=1, dtype=np.float32)

n = vectors.shape[0]
block_size = 1024
total = 0.0

for i in range(0, n, block_size):
    i_end = min(i + block_size, n)
    left = vectors[i:i_end]
    left_norms = norms[i:i_end]

    for j in range(i, n, block_size):
        j_end = min(j + block_size, n)
        right = vectors[j:j_end]

        distances = np.empty((i_end - i, j_end - j), dtype=np.float32)
        np.matmul(left, right.T, out=distances)
        distances *= np.float32(-2.0)
        distances += left_norms[:, None]
        distances += norms[j:j_end][None, :]
        np.maximum(distances, np.float32(0.0), out=distances)

        if i == j:
            np.fill_diagonal(distances, np.float32(0.0))

        np.sqrt(distances, out=distances)
        block_sum = float(np.sum(distances, dtype=np.float64))
        total += block_sum if i == j else 2.0 * block_sum

print(f"TOTAL:{total}")
