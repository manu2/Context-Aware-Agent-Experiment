import numpy as np

def main():
    X = np.load("vectors.npy", mmap_mode="r")  # (8000, 1024) float32
    n = X.shape[0]

    # Precompute squared norms in float64 for accuracy
    # Process in chunks to keep norms computation cheap
    sq_norms = np.empty(n, dtype=np.float64)
    norm_chunk = 1000
    for start in range(0, n, norm_chunk):
        end = min(start + norm_chunk, n)
        block = X[start:end].astype(np.float64)
        sq_norms[start:end] = np.einsum('ij,ij->i', block, block)

    total = 0.0
    chunk_size = 250  # tuned to keep memory usage low

    Xf = X  # memmap, will be sliced and cast per-chunk

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        A = Xf[start:end].astype(np.float64)  # (c, 1024)
        # dot products between A and all rows
        dots = A @ Xf[:].astype(np.float64).T  # This would be too big; avoid full cast
        # Not used; replaced below
        pass

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
