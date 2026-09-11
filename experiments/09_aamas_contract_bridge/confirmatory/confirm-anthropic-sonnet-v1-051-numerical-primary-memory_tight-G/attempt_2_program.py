import numpy as np
import math

def main():
    X = np.load('vectors.npy')  # float32, shape (8000, 1024)
    n = X.shape[0]

    # Convert to float64 once for accurate arithmetic; 8000*1024*8 bytes ~= 64MB
    X64 = X.astype(np.float64)

    # Squared norms of each row (float64)
    sqnorms = np.einsum('ij,ij->i', X64, X64)

    total = 0.0
    c = 0.0  # Kahan compensation

    chunk_size = 200  # tune to keep memory bounded: chunk_size * n * 8 bytes

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        Xi = X64[start:end]                     # (b, 1024)
        # dot products between chunk rows and all rows
        dot = Xi @ X64.T                         # (b, n) float64

        dist_sq = sqnorms[start:end, None] + sqnorms[None, :] - 2.0 * dot
        # Numerical noise can make tiny negatives; clip to zero
        np.maximum(dist_sq, 0.0, out=dist_sq)
        np.sqrt(dist_sq, out=dist_sq)

        # Sum this block's contribution using NumPy's pairwise summation first
        block_sum = float(np.sum(dist_sq))

        # Kahan summation across blocks for extra precision
        y = block_sum - c
        t = total + y
        c = (t - total) - y
        total = t

        del dot, dist_sq

    # Print as exact decimal value (float -> repr with full precision)
    print(f"TOTAL:{total!r}")

if __name__ == '__main__':
    main()
