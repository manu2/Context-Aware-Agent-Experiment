import numpy as np

x = np.load("vectors_secondary.npy")
norms = np.einsum("ij,ij->i", x, x, dtype=np.float32, optimize=True)

n = x.shape[0]
block_size = 256
total = 0.0

for start in range(0, n, block_size):
    end = min(start + block_size, n)
    rows = x[start:end]
    tail = x[start:]

    distances = rows @ tail.T
    distances *= -2.0
    distances += norms[start:end, None]
    distances += norms[start:]
    np.maximum(distances, 0.0, out=distances)
    np.sqrt(distances, out=distances)

    m = end - start
    diagonal_indices = np.arange(m)
    distances[diagonal_indices, diagonal_indices] = 0.0

    all_sum = distances.sum(dtype=np.float64)
    diagonal_block_sum = distances[:, :m].sum(dtype=np.float64)
    total += 2.0 * all_sum - diagonal_block_sum

print(f"TOTAL:{total}")
