import numpy as np

def main():
    # Load data without modifying the original file
    X = np.load('vectors.npy')
    X = X.astype(np.float64, copy=True)  # promote to double precision for accurate accumulation

    n = X.shape[0]

    # Precompute squared norms of each row
    sq_norms = np.einsum('ij,ij->i', X, X)

    total = 0.0

    # Process in blocks to balance memory usage and speed
    block_size = 500
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        Xb = X[start:end]

        # Compute dot products between block rows and all rows
        dots = Xb @ X.T  # shape (block, n)

        # Squared distances via ||a||^2 + ||b||^2 - 2*a.b
        d2 = sq_norms[start:end][:, None] + sq_norms[None, :] - 2.0 * dots

        # Numerical safety: clip tiny negative values due to floating point error
        np.maximum(d2, 0.0, out=d2)

        d = np.sqrt(d2)

        total += d.sum()

    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
