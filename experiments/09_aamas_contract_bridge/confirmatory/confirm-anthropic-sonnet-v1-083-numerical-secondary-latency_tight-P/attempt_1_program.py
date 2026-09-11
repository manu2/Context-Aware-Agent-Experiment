import numpy as np

def main():
    X = np.load("vectors_secondary.npy", mmap_mode="r")
    X = np.asarray(X, dtype=np.float32)  # ensure in-memory, float32 for fast BLAS matmul
    n, d = X.shape

    # Precompute squared norms in float64 for good precision
    norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)

    total = 0.0
    block_size = 400  # tuned to keep memory and time bounded

    Xt = X.T  # (d, n) view, used for matmul

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        Xb = X[start:end]  # (b, d) float32

        # Gram matrix block (b, n) computed in float32 (fast BLAS),
        # then combined with float64 norms for accuracy.
        G = Xb @ Xt  # float32 result (b, n)
        G64 = G.astype(np.float64)

        nb = norms[start:end]
        dist2 = nb[:, None] + norms[None, :] - 2.0 * G64

        # Numerical safety: clip tiny negative values caused by float error
        np.maximum(dist2, 0.0, out=dist2)

        dist = np.sqrt(dist2)
        total += dist.sum()

    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
