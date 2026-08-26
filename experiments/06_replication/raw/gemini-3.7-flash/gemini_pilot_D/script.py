import numpy as np

def compute_total_pairwise_distance(filename="vectors.npy", chunk_size=500):
    # Load vectors using memory mapping to minimize RAM overhead
    V = np.load(filename, mmap_mode="r")
    n, d = V.shape

    # Precompute squared L2 norms for each vector in chunks
    sq_norms = np.empty(n, dtype=np.float32)
    for i in range(0, n, chunk_size):
        end_i = min(i + chunk_size, n)
        sq_norms[i:end_i] = np.sum(V[i:end_i] ** 2, axis=1)

    total_dist = 0.0

    # Process in chunks using GEMM for maximum performance under memory limits
    for i in range(0, n, chunk_size):
        end_i = min(i + chunk_size, n)
        v_chunk = V[i:end_i]

        # Compute dot products: (B, D) @ (D, N) -> (B, N)
        dot = np.dot(v_chunk, V.T)

        # In-place distance calculation: ||u - v||^2 = ||u||^2 + ||v||^2 - 2(u . v)
        dot *= -2.0
        dot += sq_norms[i:end_i, None]
        dot += sq_norms[None, :]

        # Explicitly set diagonal elements (i == j) to 0.0 to prevent floating-point noise
        dot[np.arange(end_i - i), np.arange(i, end_i)] = 0.0

        # Numerical stability: clamp small negative values from precision errors to 0
        np.maximum(dot, 0.0, out=dot)
        np.sqrt(dot, out=dot)

        # Accumulate total distance in float64 precision
        total_dist += float(np.sum(dot, dtype=np.float64))

    return total_dist

if __name__ == "__main__":
    total_dist = compute_total_pairwise_distance("vectors.npy")
    print(f"TOTAL_DIST:{total_dist}")
