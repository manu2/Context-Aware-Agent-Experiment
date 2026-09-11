import numpy as np

def main():
    X = np.load('vectors.npy')  # shape (8000, 1024), float32
    n = X.shape[0]

    # Precompute squared norms of each row (float64 for accuracy)
    norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)

    total = 0.0
    block = 250  # rows per block, keeps memory bounded

    Xt = X.T  # view, no copy

    for start in range(0, n, block):
        end = min(start + block, n)
        Xi = X[start:end]  # (b, 1024)

        # dot products between block rows and all rows
        dots = Xi @ Xt  # (b, n), float32 matmul (fast BLAS)
        dots = dots.astype(np.float64)

        d2 = norms[start:end, None] + norms[None, :] - 2.0 * dots
        np.maximum(d2, 0.0, out=d2)  # guard against tiny negative values from float error

        d = np.sqrt(d2)
        total += d.sum()

    # total is a float64 scalar; print with full decimal representation
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
