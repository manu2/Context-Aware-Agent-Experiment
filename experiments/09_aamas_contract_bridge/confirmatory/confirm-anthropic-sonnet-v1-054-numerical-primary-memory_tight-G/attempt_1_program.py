import numpy as np

def main():
    X = np.load("vectors.npy", mmap_mode="r")
    N, D = X.shape

    # Work in float64 for numerical precision, load full array once (64MB for 8000x1024)
    X64 = np.asarray(X, dtype=np.float64)

    norms = np.einsum('ij,ij->i', X64, X64)  # squared norms, shape (N,)

    total = 0.0
    block_size = 500  # tune for memory/speed balance

    for start in range(0, N, block_size):
        end = min(start + block_size, N)
        block = X64[start:end]                     # (b, D)
        dot = block @ X64.T                         # (b, N)
        # squared distances: ||a||^2 + ||b||^2 - 2 a.b
        d2 = norms[start:end, None] + norms[None, :] - 2.0 * dot
        np.maximum(d2, 0.0, out=d2)                 # guard against tiny negatives
        np.sqrt(d2, out=d2)
        total += np.sum(d2, dtype=np.float64)

    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
