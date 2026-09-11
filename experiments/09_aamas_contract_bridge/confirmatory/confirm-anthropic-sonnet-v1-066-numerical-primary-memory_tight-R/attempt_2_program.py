import numpy as np

def main():
    X = np.load('vectors.npy', mmap_mode='r')  # (8000, 1024) float32
    n = X.shape[0]

    # Compute in float64 for accuracy, but keep memory usage low by
    # working on row blocks rather than materializing full arrays at once.
    Xf = np.asarray(X, dtype=np.float64)  # ~64MB, needed for BLAS speed
    norms = np.einsum('ij,ij->i', Xf, Xf)  # (n,) float64

    total = np.float64(0.0)
    block_size = 500  # tune to keep memory usage low

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = Xf[start:end]  # (b, 1024)

        # dot products between block rows and all rows
        dots = block @ Xf.T  # (b, n) float64, e.g. 500*8000*8 = 32MB

        # squared distances: ||xi||^2 + ||xj||^2 - 2*xi.xj
        sq = norms[start:end, None] + norms[None, :] - 2.0 * dots

        # numerical noise can make tiny negatives; clip to zero
        np.maximum(sq, 0.0, out=sq)

        dist = np.sqrt(sq)

        total += dist.sum(dtype=np.float64)

        # free memory explicitly
        del dots, sq, dist

    # Print as exact decimal value of the float64 total
    # Use repr-like formatting with full precision, but as plain decimal
    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
