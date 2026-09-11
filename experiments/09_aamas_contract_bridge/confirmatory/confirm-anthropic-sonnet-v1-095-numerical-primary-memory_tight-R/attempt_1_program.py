import numpy as np

def main():
    X = np.load('vectors.npy').astype(np.float64)
    N, D = X.shape

    norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    B = 500  # block size for memory efficiency

    for start in range(0, N, B):
        end = min(start + B, N)
        Xi = X[start:end]
        G = Xi @ X.T
        d2 = norms[start:end, None] + norms[None, :] - 2.0 * G
        np.maximum(d2, 0.0, out=d2)
        d = np.sqrt(d2)
        total += d.sum(dtype=np.float64)

    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
