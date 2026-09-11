import numpy as np

def main():
    X = np.load('vectors.npy', mmap_mode='r')
    X = np.asarray(X, dtype=np.float64)
    n = X.shape[0]

    norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    block_size = 500

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = X[start:end]

        dots = block @ X.T

        d2 = norms[start:end, None] + norms[None, :] - 2.0 * dots
        np.maximum(d2, 0.0, out=d2)
        np.sqrt(d2, out=d2)

        total += d2.sum()

    print(f"TOTAL:{total:.6f}")

if __name__ == '__main__':
    main()
