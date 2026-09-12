import numpy as np

def main():
    # Load full array into RAM (float32, ~31 MB) - fits comfortably in the 128MB budget.
    X = np.load('vectors.npy', mmap_mode=None)
    X = np.ascontiguousarray(X, dtype=np.float32)
    n = X.shape[0]

    # Precompute squared norms of each row (float64 for numerical stability).
    norms = np.empty(n, dtype=np.float64)
    chunk = 1000
    for i in range(0, n, chunk):
        blk = X[i:i+chunk].astype(np.float64)
        norms[i:i+chunk] = np.einsum('ij,ij->i', blk, blk)

    B = 500  # block size, chosen to keep memory and compute manageable
    total_offdiag = 0.0

    for bi in range(0, n, B):
        ib = min(B, n - bi)
        xb = X[bi:bi+ib]
        normb = norms[bi:bi+ib]

        for bj in range(bi, n, B):
            jb = min(B, n - bj)
            xc = X[bj:bj+jb]
            normc = norms[bj:bj+jb]

            # Dot product block, computed in float32 for speed (BLAS-backed).
            dot = xb @ xc.T  # shape (ib, jb), float32

            # Squared distances via ||a||^2 + ||b||^2 - 2*a.b, using float64 norms.
            d2 = normb[:, None] + normc[None, :] - 2.0 * dot.astype(np.float64)
            np.maximum(d2, 0.0, out=d2)
            d = np.sqrt(d2)

            if bi == bj:
                # only strictly upper triangle within this diagonal block (i < j)
                iu = np.triu_indices(ib, k=1)
                total_offdiag += d[iu].sum()
            else:
                # entire block, since bj > bi means all these are i<j pairs
                total_offdiag += d.sum()

    # Each unordered pair (i<j) counted once above; ordered pairs = 2x that,
    # diagonal (i==i) contributes zero and is not included/needed separately.
    total = 2.0 * total_offdiag

    print(f"TOTAL:{total:.6f}")

if __name__ == "__main__":
    main()
