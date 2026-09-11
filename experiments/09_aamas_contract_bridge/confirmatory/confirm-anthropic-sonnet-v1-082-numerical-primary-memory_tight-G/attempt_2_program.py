import numpy as np

def main():
    # Load vectors, keep as float32 to save memory during load
    vecs32 = np.load("vectors.npy", mmap_mode=None)
    n = vecs32.shape[0]

    # Convert to float64 once for accurate distance computation
    vecs = vecs32.astype(np.float64)
    del vecs32

    # Precompute squared norms
    norms = np.einsum('ij,ij->i', vecs, vecs)

    total = 0.0
    chunk_size = 1000  # tune for memory: chunk_size * n * 8 bytes

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        chunk = vecs[start:end]  # (c, d)

        # Compute squared distances: ||a||^2 + ||b||^2 - 2 a.b
        dot = chunk @ vecs.T  # (c, n)
        sq_dist = norms[start:end, None] + norms[None, :] - 2.0 * dot
        del dot

        # Numerical safety: clip small negative values due to floating point error
        np.maximum(sq_dist, 0.0, out=sq_dist)

        dist = np.sqrt(sq_dist, out=sq_dist)
        total += dist.sum(dtype=np.float64)

        del sq_dist, dist, chunk

    # total is sum over ordered pairs (i,j) including diagonal (which is zero)
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
