import numpy as np

def main():
    vectors = np.load('vectors.npy', mmap_mode='r')
    n = vectors.shape[0]

    # Use float64 for accurate computation
    v = vectors.astype(np.float64)

    sq_norms = np.einsum('ij,ij->i', v, v)

    total = 0.0
    chunk_size = 500

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        chunk = v[start:end]  # (c, d)

        # Compute squared distances: ||a||^2 + ||b||^2 - 2 a.b
        dots = chunk @ v.T  # (c, n)
        dist_sq = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots

        # Numerical issues can cause tiny negative values due to floating point
        np.maximum(dist_sq, 0.0, out=dist_sq)

        dist = np.sqrt(dist_sq)
        total += dist.sum(dtype=np.float64)

    # Print with high precision decimal representation
    result_str = np.format_float_positional(total, precision=17, unique=True, trim='0')
    print(f"TOTAL:{result_str}")

if __name__ == '__main__':
    main()
