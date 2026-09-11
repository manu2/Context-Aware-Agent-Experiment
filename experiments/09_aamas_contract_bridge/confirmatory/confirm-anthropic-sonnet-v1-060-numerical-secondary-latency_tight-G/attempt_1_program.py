import numpy as np

def main():
    X = np.load('vectors_secondary.npy')
    X = X.astype(np.float64, copy=False)
    n = X.shape[0]
    sq_norms = np.einsum('ij,ij->i', X, X)

    block_size = 500
    total = 0.0

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        Xb = X[start:end]
        # dot products between block and all rows
        dots = Xb @ X.T  # shape (block, n)
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots
        np.maximum(d2, 0.0, out=d2)
        d = np.sqrt(d2)
        total += d.sum()

    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
