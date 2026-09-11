import numpy as np


def main():
    # Load input vectors
    arr = np.load("vectors_secondary.npy")
    N = arr.shape[0]

    # Convert to float64 to ensure high numerical precision and prevent overflow/underflow
    X = arr.astype(np.float64)
    sq_norms = np.sum(X**2, axis=1, keepdims=True)

    total_distance = 0.0
    batch_size = 1000

    # Process in row blocks to keep peak memory usage low (~150 MB)
    for i in range(0, N, batch_size):
        end_i = min(i + batch_size, N)
        X_blk = X[i:end_i]

        # ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * <x_i, x_j>
        d2 = sq_norms[i:end_i] + sq_norms.T
        d2 -= 2.0 * (X_blk @ X.T)

        # Numerical clamping to avoid negative values from floating point roundoff
        np.maximum(d2, 0.0, out=d2)

        # Zero out the diagonal explicitly
        diag_idx = np.arange(end_i - i)
        d2[diag_idx, i + diag_idx] = 0.0

        np.sqrt(d2, out=d2)
        total_distance += float(np.sum(d2))

    print(f"TOTAL:{total_distance}")


if __name__ == "__main__":
    main()
