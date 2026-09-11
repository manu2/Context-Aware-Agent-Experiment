import numpy as np

def main():
    X = np.load('vectors.npy')  # (8000, 1024) float32
    X = X.astype(np.float64, copy=False)
    n = X.shape[0]

    norms2 = np.einsum('ij,ij->i', X, X)  # squared norms, float64

    total = 0.0
    chunk_size = 250  # tuned for memory/speed balance

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        Xc = X[start:end]                     # (m, d)
        dot = Xc @ X.T                        # (m, n)
        d2 = norms2[start:end, None] + norms2[None, :] - 2.0 * dot
        np.maximum(d2, 0.0, out=d2)            # numerical safety
        np.sqrt(d2, out=d2)
        total += d2.sum(dtype=np.float64)

    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
