import numpy as np

def main():
    X = np.load("vectors.npy", mmap_mode="r")
    X = np.asarray(X, dtype=np.float32)
    n = X.shape[0]

    norms = np.einsum('ij,ij->i', X, X, dtype=np.float32)

    total = np.float64(0.0)
    chunk = 400  # rows per block, tuned for memory/speed tradeoff

    Xt = X.T  # view, no copy (float32 contiguous transpose view)

    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        Xb = X[start:end]                       # (b, d)
        G = Xb @ Xt                              # (b, n) float32, BLAS matmul
        d2 = norms[start:end, None] + norms[None, :] - 2.0 * G
        np.maximum(d2, 0.0, out=d2)
        np.sqrt(d2, out=d2)
        total += d2.sum(dtype=np.float64)

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
