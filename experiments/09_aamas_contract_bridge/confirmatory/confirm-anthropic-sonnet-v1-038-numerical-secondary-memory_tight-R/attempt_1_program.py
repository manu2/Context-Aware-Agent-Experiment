import numpy as np

def main():
    X = np.load('vectors_secondary.npy')
    X = X.astype(np.float64, copy=False)
    n = X.shape[0]

    sq_norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    block_size = 500

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        Xb = X[start:end]

        # Dot products between block rows and all rows
        gram = Xb @ X.T  # shape (block, n)

        # Squared distances: ||a||^2 + ||b||^2 - 2 a.b
        dist_sq = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * gram

        # Numerical safety: clip small negative values to zero
        np.maximum(dist_sq, 0.0, out=dist_sq)

        dist = np.sqrt(dist_sq)

        total += dist.sum()

    # Print with high precision decimal formatting
    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
