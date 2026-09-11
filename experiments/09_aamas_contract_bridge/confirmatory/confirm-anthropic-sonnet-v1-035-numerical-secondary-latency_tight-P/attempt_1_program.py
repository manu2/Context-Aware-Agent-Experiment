import numpy as np

def main():
    X = np.load('vectors_secondary.npy', mmap_mode=None)
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    n = X.shape[0]

    # Precompute squared norms in float64 for accuracy
    norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)

    Xt = X.T  # shape (1024, n), used for matmul

    total = 0.0
    block = 1000  # rows per block, tune for memory/time balance

    for start in range(0, n, block):
        end = min(start + block, n)
        Xb = X[start:end]  # (b, 1024) float32

        # Dot products between block rows and all rows: (b, n) float32
        dot = Xb @ Xt  # BLAS matmul, float32

        # Compute squared distances in float64 for numerical stability
        dot64 = dot.astype(np.float64)
        nb = norms[start:end]  # (b,)
        sq_dist = nb[:, None] + norms[None, :] - 2.0 * dot64

        # Clip tiny negative values due to floating point error
        np.maximum(sq_dist, 0.0, out=sq_dist)

        dist = np.sqrt(sq_dist)

        total += dist.sum(dtype=np.float64)

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
