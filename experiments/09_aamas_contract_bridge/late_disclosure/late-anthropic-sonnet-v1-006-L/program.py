import numpy as np

def main():
    X = np.load('vectors.npy', mmap_mode='r')  # (8000, 1024) float32
    n, d = X.shape

    # Precompute squared norms in double precision for accuracy
    norms = np.empty(n, dtype=np.float64)
    block_norm = 500
    for start in range(0, n, block_norm):
        end = min(start + block_norm, n)
        chunk = np.asarray(X[start:end], dtype=np.float64)
        norms[start:end] = np.einsum('ij,ij->i', chunk, chunk)

    total = 0.0
    block = 100  # rows per block, keeps memory bounded

    # Load full X into a normal float32 array once (32 MB), reused for all blocks
    Xf = np.asarray(X, dtype=np.float32)

    for start in range(0, n, block):
        end = min(start + block, n)
        A = Xf[start:end]  # (b, d) float32

        # dot products between A and all rows, float32 result to save memory
        dots = A.dot(Xf.T)  # (b, n) float32

        # combine with norms (double precision) to get squared distances
        dots64 = dots.astype(np.float64)
        sq = norms[start:end][:, None] + norms[None, :] - 2.0 * dots64
        np.maximum(sq, 0.0, out=sq)  # guard against tiny negative values
        dist = np.sqrt(sq)

        total += float(dist.sum())

        del dots, dots64, sq, dist

    print(f"TOTAL:{total}")

if __name__ == '__main__':
    main()
