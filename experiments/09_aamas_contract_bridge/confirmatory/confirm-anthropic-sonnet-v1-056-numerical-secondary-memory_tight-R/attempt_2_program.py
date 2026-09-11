import numpy as np

def main():
    X = np.load("vectors_secondary.npy", mmap_mode="r")
    n = X.shape[0]

    # Precompute squared norms for all rows (float64 for accuracy)
    # Load in chunks to avoid excessive memory use from full float64 copy
    norm_chunk = 1000
    sq_norms = np.empty(n, dtype=np.float64)
    for start in range(0, n, norm_chunk):
        end = min(start + norm_chunk, n)
        block = X[start:end].astype(np.float64)
        sq_norms[start:end] = np.einsum('ij,ij->i', block, block)

    total = 0.0
    chunk_size = 200  # rows per outer chunk

    for i0 in range(0, n, chunk_size):
        i1 = min(i0 + chunk_size, n)
        Xi = X[i0:i1].astype(np.float64)  # (b, d)
        sq_i = sq_norms[i0:i1]  # (b,)

        for j0 in range(0, n, chunk_size):
            j1 = min(j0 + chunk_size, n)
            Xj = X[j0:j1].astype(np.float64)  # (c, d)
            sq_j = sq_norms[j0:j1]  # (c,)

            # squared distances: ||xi||^2 + ||xj||^2 - 2 xi.xj
            dot = Xi @ Xj.T  # (b, c)
            sq_dist = sq_i[:, None] + sq_j[None, :] - 2.0 * dot
            np.maximum(sq_dist, 0.0, out=sq_dist)  # avoid tiny negatives from fp error
            dist = np.sqrt(sq_dist)
            total += dist.sum()

    # Print with full precision decimal formatting
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
