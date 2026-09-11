import numpy as np


def main():
    X = np.load("vectors_secondary.npy")
    n_rows, _ = X.shape

    # Precompute squared norms in small batches to preserve memory
    norms_sq = np.empty(n_rows, dtype=np.float32)
    for i in range(0, n_rows, 1000):
        norms_sq[i : i + 1000] = np.sum(X[i : i + 1000] ** 2, axis=1)

    total = 0.0
    batch_size = 800

    # Process in blocks of 800 rows
    for i1 in range(0, n_rows, batch_size):
        i2 = min(i1 + batch_size, n_rows)
        nrows_chunk = i2 - i1

        # GEMM: (nrows_chunk, 1024) @ (1024, 8000) -> (nrows_chunk, 8000) float32
        dot = X[i1:i2] @ X.T

        # In-place calculation: ||u - v||^2 = ||u||^2 + ||v||^2 - 2 <u, v>
        dot *= -2.0
        dot += norms_sq[i1:i2, None]
        dot += norms_sq[None, :]
        np.maximum(dot, 0.0, out=dot)

        # Ensure exact zero on the diagonal to eliminate rounding artifacts
        dot[np.arange(nrows_chunk), np.arange(i1, i2)] = 0.0

        np.sqrt(dot, out=dot)
        total += float(np.sum(dot, dtype=np.float64))
        del dot

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
