import numpy as np

def main():
    # Memory-map the input to avoid loading it fully into RAM as float64
    vectors = np.load('vectors.npy', mmap_mode='r')  # shape (8000, 1024), float32
    n = vectors.shape[0]

    # Compute squared norms in float64, using chunks to limit memory
    norm_block = 1000
    norms = np.empty(n, dtype=np.float64)
    for start in range(0, n, norm_block):
        end = min(start + norm_block, n)
        chunk = vectors[start:end].astype(np.float64)
        norms[start:end] = np.einsum('ij,ij->i', chunk, chunk)

    total = 0.0
    row_block = 200  # process this many rows at a time to bound memory

    for start in range(0, n, row_block):
        end = min(start + row_block, n)
        block = vectors[start:end].astype(np.float64)  # (b, 1024)

        # Compute dot products between this block and all rows, in column-chunks
        col_block = 2000
        dist_sum_block = np.zeros(end - start, dtype=np.float64)

        for cstart in range(0, n, col_block):
            cend = min(cstart + col_block, n)
            other = vectors[cstart:cend].astype(np.float64)  # (c, 1024)

            dots = block @ other.T  # (b, c)

            sq_dists = norms[start:end, None] + norms[None, cstart:cend] - 2.0 * dots
            np.maximum(sq_dists, 0.0, out=sq_dists)
            dists = np.sqrt(sq_dists)

            dist_sum_block += dists.sum(axis=1)

            del other, dots, sq_dists, dists

        total += dist_sum_block.sum()
        del block, dist_sum_block

    # Format as decimal (total is a float64 sum)
    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
