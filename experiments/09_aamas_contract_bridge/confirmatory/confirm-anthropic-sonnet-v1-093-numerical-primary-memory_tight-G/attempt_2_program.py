import numpy as np

def main():
    # Load as float32 to save memory initially
    vecs32 = np.load('vectors.npy', mmap_mode='r')
    n, d = vecs32.shape

    # Convert to float64 once for accurate computation (manageable size: n*d*8 bytes)
    vecs = np.asarray(vecs32, dtype=np.float64)

    # Precompute squared norms
    norms = np.einsum('ij,ij->i', vecs, vecs)

    vecs_T = vecs.T  # (d, n), still float64, view/transpose (no copy needed for matmul)

    total = 0.0
    block_size = 500  # tune for memory/time balance

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vecs[start:end]  # (b, d)

        # Compute dot products: (b, n)
        dots = block @ vecs_T

        # Squared distances: ||a||^2 + ||b||^2 - 2*a.b
        block_norms = norms[start:end][:, None]
        sq_dists = block_norms + norms[None, :] - 2.0 * dots

        # Numerical safety: clip small negative values due to floating point errors
        np.maximum(sq_dists, 0.0, out=sq_dists)

        dists = np.sqrt(sq_dists)
        total += dists.sum()

        # Free memory explicitly
        del dots, sq_dists, dists, block

    print(f"TOTAL:{total:.0f}" if total == int(total) else f"TOTAL:{total}")

if __name__ == "__main__":
    main()
