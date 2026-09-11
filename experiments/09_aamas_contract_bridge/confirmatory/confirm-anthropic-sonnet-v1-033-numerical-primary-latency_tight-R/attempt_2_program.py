import numpy as np

def main():
    X = np.load("vectors.npy", mmap_mode="r")  # (8000, 1024) float32
    n = X.shape[0]

    # Load into memory as float64 for accurate dot products
    X64 = np.asarray(X, dtype=np.float64)

    sq_norms = np.einsum('ij,ij->i', X64, X64)

    total = 0.0
    chunk_size = 500  # tune for memory/speed balance

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        block = X64[start:end]  # (chunk, 1024)

        # Compute dot products between block and all rows
        dots = block @ X64.T  # (chunk, n)

        # squared distances: ||a||^2 + ||b||^2 - 2 a.b
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots

        # Numerical safety: clip small negatives to zero
        np.maximum(d2, 0.0, out=d2)

        d = np.sqrt(d2)

        total += d.sum()

    # total is a Python float; format as decimal
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
