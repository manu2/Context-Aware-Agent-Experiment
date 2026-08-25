import numpy as np

def main():
    V = np.load('vectors.npy')
    if V.dtype != np.float32:
        V = V.astype(np.float32)

    n = V.shape[0]
    norms = np.einsum('ij,ij->i', V, V)

    total = 0.0
    block_size = 500
    if block_size > n:
        block_size = n

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = V[start:end]
        dot = block @ V.T
        block_norms = norms[start:end][:, None]
        dist_sq = block_norms + norms[None, :] - 2.0 * dot
        np.maximum(dist_sq, 0.0, out=dist_sq)
        dist = np.sqrt(dist_sq, dtype=np.float64)
        total += float(np.sum(dist))
        del dot, dist_sq, dist, block

    print(f'TOTAL_DIST:{total}')

if __name__ == '__main__':
    main()
