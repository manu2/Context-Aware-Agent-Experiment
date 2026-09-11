import numpy as np

def main():
    X = np.load('vectors.npy')  # 8000 x 1024, float32
    X = X.astype(np.float64, copy=False)
    n = X.shape[0]

    sq_norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    block_size = 500

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        Xi = X[start:end]
        dot = Xi @ X.T  # (block, n)
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dot
        np.maximum(d2, 0.0, out=d2)
        d = np.sqrt(d2)
        total += d.sum(dtype=np.float64)

    print(f"TOTAL:{total!r}")

if __name__ == '__main__':
    main()
