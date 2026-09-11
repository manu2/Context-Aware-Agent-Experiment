import numpy as np

def main():
    X = np.load('vectors.npy', mmap_mode='r')
    n = X.shape[0]

    # Load into memory as float32 (should be small: 8000*1024*4 bytes ~ 32MB)
    X = np.asarray(X, dtype=np.float32)

    # Precompute squared norms in float64 for accuracy
    sq_norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)

    total = np.float64(0.0)

    block_size = 500
    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = X[start:end]  # (b, d) float32

        # Compute dot products between block and all rows: (b, n) float32
        dots = block @ X.T  # float32 matmul (BLAS, efficient)
        dots = dots.astype(np.float64)

        # Compute squared distances: ||a||^2 + ||b||^2 - 2*a.b
        b_norms = sq_norms[start:end].reshape(-1, 1)
        sq_dists = b_norms + sq_norms.reshape(1, -1) - 2.0 * dots

        # Numerical safety: clip small negative values to zero
        np.maximum(sq_dists, 0.0, out=sq_dists)

        dists = np.sqrt(sq_dists)

        total += dists.sum(dtype=np.float64)

        # Free memory explicitly
        del dots, sq_dists, dists, block

    # Format total as exact decimal value (float64 precision)
    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
