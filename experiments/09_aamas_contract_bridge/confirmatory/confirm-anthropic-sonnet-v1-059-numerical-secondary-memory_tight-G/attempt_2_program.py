import numpy as np

def main():
    X = np.load("vectors_secondary.npy", mmap_mode="r")
    n = X.shape[0]

    # Load once as float64 for accurate norm/dot computations, but keep footprint modest.
    Xd = X.astype(np.float64, copy=True)  # 8000*1024*8 bytes ~ 65MB, fine
    sq_norms = np.einsum('ij,ij->i', Xd, Xd)

    total = 0.0
    block_size = 500  # controls memory of block x n distance matrix

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = Xd[start:end]  # (b, d)

        # dot products between block and all rows: (b, n)
        dots = block @ Xd.T

        # squared distances: ||xi||^2 + ||xj||^2 - 2 xi.xj
        b_norms = sq_norms[start:end][:, None]
        sq_dists = b_norms + sq_norms[None, :] - 2.0 * dots

        # numerical safety: clip small negatives due to floating point error
        np.maximum(sq_dists, 0.0, out=sq_dists)

        dists = np.sqrt(sq_dists)
        total += dists.sum()

        del dots, sq_dists, dists, block

    # Print as decimal value
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
