import numpy as np

def main():
    X = np.load('vectors.npy', mmap_mode='r')
    X = np.asarray(X, dtype=np.float64)
    n = X.shape[0]

    sq_norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    chunk_size = 500

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        block = X[start:end]  # (b, d)

        # Compute squared distances: ||a||^2 + ||b||^2 - 2 a.b
        dots = block @ X.T  # (b, n)
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots
        np.maximum(d2, 0.0, out=d2)  # avoid tiny negative due to floating point
        d = np.sqrt(d2)

        total += np.sum(d, dtype=np.float64)

    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
