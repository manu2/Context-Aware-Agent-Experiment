import numpy as np

def main():
    X = np.load('vectors.npy', mmap_mode='r')
    X = np.asarray(X, dtype=np.float32)  # ensure contiguous float32 array
    n = X.shape[0]

    # squared norms of each row
    norms = np.einsum('ij,ij->i', X, X, dtype=np.float32)

    # Gram matrix via single BLAS call (float32 for speed/memory)
    G = X @ X.T   # shape (n, n), float32

    # dist_sq[i,j] = norms[i] + norms[j] - 2*G[i,j]
    # do this in-place to save memory
    G *= -2.0
    G += norms[:, None]
    G += norms[None, :]

    # numerical noise can make tiny negatives -> clip
    np.maximum(G, 0.0, out=G)

    np.sqrt(G, out=G)

    total = np.sum(G, dtype=np.float64)

    print(f"TOTAL:{total:.10f}".rstrip('0').rstrip('.') if False else f"TOTAL:{total}")

if __name__ == '__main__':
    main()
