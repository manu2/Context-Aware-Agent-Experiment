import math
import numpy as np

BLOCK_SIZE = 256

source = np.load("vectors_secondary.npy", mmap_mode="r", allow_pickle=False)
vectors = np.array(source, dtype=np.float64, order="C", copy=True)
del source

row_norms = np.einsum("ij,ij->i", vectors, vectors, optimize=True)
n = vectors.shape[0]
partial_sums = []

for start in range(0, n, BLOCK_SIZE):
    stop = min(start + BLOCK_SIZE, n)
    block_len = stop - start

    distances = vectors[start:stop] @ vectors[start:].T
    distances *= -2.0
    distances += row_norms[start:stop, None]
    distances += row_norms[None, start:]
    np.maximum(distances, 0.0, out=distances)

    diagonal = np.arange(block_len)
    distances[diagonal, diagonal] = 0.0
    np.sqrt(distances, out=distances)

    partial_sums.append(float(np.sum(distances[:, :block_len], dtype=np.float64)))
    if block_len < distances.shape[1]:
        partial_sums.append(
            2.0 * float(np.sum(distances[:, block_len:], dtype=np.float64))
        )

total = math.fsum(partial_sums)
print("TOTAL:" + repr(total))
