import numpy as np

x = np.load("vectors.npy", allow_pickle=False)
norms = np.einsum("ij,ij->i", x, x, optimize=True)

n = x.shape[0]
block_size = 800
work = np.empty((block_size, block_size), dtype=np.float32)
total = 0.0

for i in range(0, n, block_size):
    a = x[i:i + block_size]
    ni = norms[i:i + block_size]

    for j in range(i, n, block_size):
        b = x[j:j + block_size]
        nj = norms[j:j + block_size]

        np.matmul(a, b.T, out=work)
        work *= -2.0
        work += ni[:, None]
        work += nj[None, :]
        np.maximum(work, 0.0, out=work)

        if i == j:
            np.fill_diagonal(work, 0.0)

        np.sqrt(work, out=work)
        block_sum = float(np.sum(work, dtype=np.float64))
        total += block_sum if i == j else 2.0 * block_sum

print(f"TOTAL:{total:.17g}")
