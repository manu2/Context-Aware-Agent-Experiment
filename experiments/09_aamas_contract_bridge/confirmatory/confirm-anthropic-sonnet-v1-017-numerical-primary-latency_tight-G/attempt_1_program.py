import numpy as np

def main():
    vectors = np.load("vectors.npy", mmap_mode="r")
    n = vectors.shape[0]

    # Use float64 for accurate accumulation
    V = np.asarray(vectors, dtype=np.float64)

    norms = np.einsum('ij,ij->i', V, V)

    total = 0.0
    block_size = 500

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = V[start:end]  # (b, d)

        # dot products between block rows and all rows
        dots = block @ V.T  # (b, n)

        sq_dists = norms[start:end, None] + norms[None, :] - 2.0 * dots
        # numerical safety: clip small negative values to zero
        np.maximum(sq_dists, 0.0, out=sq_dists)

        dists = np.sqrt(sq_dists)
        total += dists.sum()

    # total is a Python float (from numpy float64 sum)
    total_val = float(total)
    print(f"TOTAL:{total_val!r}" if False else f"TOTAL:{total_val:.10f}".rstrip('0').rstrip('.') if False else f"TOTAL:{total_val}")

if __name__ == "__main__":
    main()
