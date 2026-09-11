import os
# Ensure single-threaded BLAS behavior to match the 1-core CPU quota
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import numpy as np

def main():
    # Load data (read-only, we won't modify it)
    X = np.load("vectors_secondary.npy")
    assert X.dtype == np.float32

    n = X.shape[0]

    # Precompute squared norms of each row (float64 for better accumulation precision)
    norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)  # shape (n,)

    total = 0.0

    block_size = 1000  # chosen to bound peak memory usage
    Xt = X.T  # view, no copy

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        Xi = X[start:end]  # (b, d) float32

        # Compute dot products between block rows and all rows
        dot = Xi @ Xt  # (b, n) float32

        # Compute squared distances: ||xi||^2 + ||xj||^2 - 2*dot
        # Use float64 for the combination to keep precision reasonable
        dist_sq = norms[start:end, None] + norms[None, :] - 2.0 * dot.astype(np.float64)

        # Numerical safety: clip tiny negative values due to floating point error
        np.maximum(dist_sq, 0.0, out=dist_sq)

        dist = np.sqrt(dist_sq)

        total += dist.sum(dtype=np.float64)

        # free memory explicitly
        del dot, dist_sq, dist

    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
