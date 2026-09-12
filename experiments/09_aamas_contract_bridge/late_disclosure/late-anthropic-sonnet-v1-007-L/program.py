import os
# Ensure BLAS/OpenMP doesn't try to oversubscribe a single core
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

def main():
    # Load data; ensure float32 contiguous array
    X = np.load("vectors.npy")
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    if not X.flags["C_CONTIGUOUS"]:
        X = np.ascontiguousarray(X)

    n = X.shape[0]

    # Squared norms of each row
    norms = np.einsum("ij,ij->i", X, X, dtype=np.float32)

    # Gram matrix via single BLAS matmul call (dominant cost)
    G = X @ X.T  # shape (n, n), float32

    # Compute squared distances in-place: D2 = norms_i + norms_j - 2*G
    # G currently holds dot products; transform into squared distances
    G *= -2.0
    G += norms[:, None]
    G += norms[None, :]

    # Numerical noise can make tiny negatives; clip to zero
    np.maximum(G, 0.0, out=G)

    # sqrt in place to get distances
    np.sqrt(G, out=G)

    # Sum everything (ordered pairs, including diagonal zeros) in float64 for precision
    total = G.sum(dtype=np.float64)

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
