import numpy as np


def main():
    # Load input vectors without modifying the file
    vectors = np.load("vectors.npy")

    # Use float64 to prevent numerical precision loss during summation
    X = vectors.astype(np.float64)
    sq_norms = np.sum(X * X, axis=1)

    n = len(X)
    chunk_size = 2000
    total = 0.0

    # Process in row chunks to balance memory usage and BLAS GEMM throughput
    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)

        # ||u - v||^2 = ||u||^2 + ||v||^2 - 2 <u, v>
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * (X[start:end] @ X.T)

        # Guard against small negative values from floating-point inaccuracies
        np.maximum(d2, 0.0, out=d2)

        # Explicitly ensure the diagonal distances are exactly zero
        np.fill_diagonal(d2[:, start:end], 0.0)

        # In-place square root and accumulation
        np.sqrt(d2, out=d2)
        total += float(np.sum(d2))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
