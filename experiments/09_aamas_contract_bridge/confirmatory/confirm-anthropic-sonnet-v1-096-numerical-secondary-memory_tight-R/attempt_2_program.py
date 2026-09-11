import numpy as np

def main():
    X = np.load("vectors_secondary.npy", mmap_mode="r")
    n, d = X.shape

    # Precompute squared norms in float64 for better numerical stability
    norms = np.empty(n, dtype=np.float64)
    block_size = 500

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = np.asarray(X[start:end], dtype=np.float64)
        norms[start:end] = np.einsum('ij,ij->i', block, block)

    total = np.float64(0.0)

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = np.asarray(X[start:end], dtype=np.float64)  # (b, d)

        # Compute dot products of this block with all rows, in chunks over columns too
        col_block_size = 2000
        dist_sq_full = np.empty((end - start, n), dtype=np.float64)

        for cstart in range(0, n, col_block_size):
            cend = min(cstart + col_block_size, n)
            other = np.asarray(X[cstart:cend], dtype=np.float64)  # (c, d)
            dots = block @ other.T  # (b, c)
            dist_sq = norms[start:end, None] + norms[cstart:cend][None, :] - 2.0 * dots
            np.maximum(dist_sq, 0.0, out=dist_sq)
            dist_sq_full[:, cstart:cend] = dist_sq

        dists = np.sqrt(dist_sq_full)
        total += dists.sum(dtype=np.float64)

    print(f"TOTAL:{total:.10f}".rstrip('0').rstrip('.') if False else f"TOTAL:{total}")

if __name__ == "__main__":
    main()
