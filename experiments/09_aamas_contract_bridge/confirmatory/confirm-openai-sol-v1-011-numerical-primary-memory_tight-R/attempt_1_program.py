import numpy as np

vectors = np.load("vectors.npy", allow_pickle=False)
x = np.asarray(vectors, dtype=np.float64)
n = x.shape[0]
norms = np.einsum("ij,ij->i", x, x, dtype=np.float64)

block_size = 512
partial_sums = []

for start_i in range(0, n, block_size):
    end_i = min(start_i + block_size, n)
    xi = x[start_i:end_i]
    ni = norms[start_i:end_i]

    for start_j in range(start_i, n, block_size):
        end_j = min(start_j + block_size, n)
        xj = x[start_j:end_j]
        nj = norms[start_j:end_j]

        squared = xi @ xj.T
        squared *= -2.0
        squared += ni[:, None]
        squared += nj[None, :]

        scale = ni[:, None] + nj[None, :]
        close = (scale > 0.0) & (squared <= scale * 1.0e-11)

        if start_i == start_j:
            close[np.tril_indices(end_i - start_i)] = False

        np.maximum(squared, 0.0, out=squared)
        distances = np.sqrt(squared, out=squared)

        rows, cols = np.nonzero(close)
        for k in range(0, rows.size, 2048):
            r = rows[k:k + 2048]
            c = cols[k:k + 2048]
            delta = xi[r] - xj[c]
            distances[r, c] = np.sqrt(
                np.einsum("ij,ij->i", delta, delta, dtype=np.float64)
            )

        if start_i == start_j:
            upper = np.triu_indices(end_i - start_i, k=1)
            partial_sums.append(
                np.sum(distances[upper], dtype=np.longdouble)
            )
        else:
            partial_sums.append(
                np.sum(distances, dtype=np.longdouble)
            )

unordered_total = np.sum(
    np.asarray(partial_sums, dtype=np.longdouble),
    dtype=np.longdouble
)
total = float(unordered_total * 2)
print("TOTAL:" + format(total, ".17g"))
