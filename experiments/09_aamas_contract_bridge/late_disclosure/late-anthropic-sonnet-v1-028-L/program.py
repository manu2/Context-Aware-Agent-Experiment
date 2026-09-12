import numpy as np

def main():
    X = np.load('vectors_secondary.npy')
    # Ensure contiguous float32 array without modifying original file on disk
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    else:
        X = np.ascontiguousarray(X)

    n = X.shape[0]

    # Precompute squared norms (float64 for better accumulation precision)
    sq_norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)

    total = 0.0
    # Choose a chunk size that keeps intermediate matrices small enough
    # to fit comfortably in memory while still using efficient BLAS calls.
    chunk = 400

    Xt = X.T  # (1024, n) view, no copy needed since X is contiguous row-major

    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        block = X[start:end]                     # (b, 1024) float32
        dot = block @ Xt                          # (b, n) float32, BLAS sgemm
        dot = dot.astype(np.float64)              # promote for precision
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dot
        np.maximum(d2, 0.0, out=d2)
        d = np.sqrt(d2)
        total += d.sum(dtype=np.float64)

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
