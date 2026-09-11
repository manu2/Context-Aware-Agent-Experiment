import numpy as np

def main():
    X = np.load('vectors.npy')  # float32, shape (8000, 1024)
    n = X.shape[0]

    # Compute squared norms with float64 precision, in chunks to limit memory
    norm_chunk = 1000
    norms = np.empty(n, dtype=np.float64)
    for start in range(0, n, norm_chunk):
        end = min(start + norm_chunk, n)
        blk = X[start:end].astype(np.float64)
        norms[start:end] = np.sum(blk * blk, axis=1)

    total = 0.0
    chunk_size = 500  # rows per block, keeps memory well under limit

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        Xi = X[start:end]  # float32, small block

        # Fast BLAS matmul in float32 for speed
        gram = Xi @ X.T  # (end-start, n), float32

        # Upcast to float64 for accurate distance computation
        gram64 = gram.astype(np.float64)
        d2 = norms[start:end, None] + norms[None, :] - 2.0 * gram64
        np.maximum(d2, 0.0, out=d2)  # guard against tiny negative values from rounding
        d = np.sqrt(d2)

        total += d.sum(dtype=np.float64)

    print(f"TOTAL:{total:.6f}")

if __name__ == "__main__":
    main()
