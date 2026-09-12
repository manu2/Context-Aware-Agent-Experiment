import numpy as np

def main():
    X = np.load('vectors_secondary.npy')
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    n = X.shape[0]

    # squared norms (float64 for later precision in subtraction)
    norms = np.einsum('ij,ij->i', X, X, dtype=np.float32).astype(np.float64)

    total = 0.0
    # Block size chosen to balance memory (<1GB) and BLAS efficiency.
    block = 1000

    Xt = X.T  # transposed view, reused for all blocks

    for start in range(0, n, block):
        end = min(start + block, n)
        Xb = X[start:end]

        # G = Xb @ X^T  -> shape (block, n), computed via single-precision BLAS (fast)
        G = Xb @ Xt  # float32

        # squared distances using float64 norms broadcast, but keep memory manageable
        d2 = norms[start:end, None] + norms[None, :] - 2.0 * G.astype(np.float64)

        # numerical safety: clip tiny negatives from floating point error
        np.maximum(d2, 0.0, out=d2)

        d = np.sqrt(d2)
        total += d.sum(dtype=np.float64)

    print(f"TOTAL:{total:.6f}")

if __name__ == "__main__":
    main()
