import numpy as np

def main():
    vecs = np.load('vectors.npy', mmap_mode='r')
    n = vecs.shape[0]

    # Work in float64 for numerical accuracy
    V = np.asarray(vecs, dtype=np.float64)
    norms_sq = np.einsum('ij,ij->i', V, V)

    total = np.float64(0.0)
    block_size = 500  # balance memory vs speed

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = V[start:end]  # (b, d)

        # dot products between block and all rows
        dots = block @ V.T  # (b, n)

        # squared distances: ||xi||^2 + ||xj||^2 - 2*xi.xj
        sq_dists = norms_sq[start:end, None] + norms_sq[None, :] - 2.0 * dots

        # numerical safety: clip tiny negative values to zero
        np.maximum(sq_dists, 0.0, out=sq_dists)

        dists = np.sqrt(sq_dists)
        total += dists.sum()

    # Print with full precision decimal representation
    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
