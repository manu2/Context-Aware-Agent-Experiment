import numpy as np

def main():
    # Load the array normally; 8000x1024 float32 ~= 32 MiB, fits comfortably.
    vecs = np.load('vectors.npy', mmap_mode='r')
    n = vecs.shape[0]

    # Compute squared norms in float64 for numerical stability.
    vecs32 = np.asarray(vecs, dtype=np.float32)
    norms = np.einsum('ij,ij->i', vecs32.astype(np.float64), vecs32.astype(np.float64))

    total = 0.0
    block_size = 200  # keeps intermediate matrices small (~ block_size*8000*4 bytes)

    vecs_T = vecs32.T  # (1024, n) view, no copy needed since vecs32 is contiguous float32

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = vecs32[start:end]  # (b, 1024) float32

        # Compute dot products block @ vecs_T -> (b, n) float32
        dots = block @ vecs_T  # float32 matmul

        # Compute squared distances: norm_i + norm_j - 2*dot
        # Use float64 for the combination to maintain precision
        block_norms = norms[start:end].reshape(-1, 1)  # (b,1) float64
        sq_dists = block_norms + norms.reshape(1, -1) - 2.0 * dots.astype(np.float64)

        # Numerical noise can make small negatives; clip
        np.maximum(sq_dists, 0.0, out=sq_dists)

        dists = np.sqrt(sq_dists)
        total += dists.sum()

        # free memory explicitly
        del dots, sq_dists, dists, block

    # Print with high precision decimal representation
    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
