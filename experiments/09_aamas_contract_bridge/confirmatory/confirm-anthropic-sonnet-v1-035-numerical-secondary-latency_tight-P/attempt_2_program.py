import numpy as np

def main():
    # Load data (float32, shape (8000, 1024))
    X = np.load('vectors_secondary.npy')
    n = X.shape[0]

    # Precompute squared norms in double precision for accuracy
    normsq = np.einsum('ij,ij->i', X, X, dtype=np.float64)

    total = 0.0
    # Process in row blocks, only computing the upper-triangular part
    # (including the diagonal) to halve the required matrix multiplications.
    # Since the matrix is symmetric and the diagonal is zero, the full sum
    # over all ordered pairs equals 2 * (sum over i <= j of dist(i,j)).
    block = 400

    for start in range(0, n, block):
        stop = min(start + block, n)
        Xi = X[start:stop]        # shape (b, d)
        Xj = X[start:]            # shape (n-start, d)

        # Matrix multiply in float32 for speed (BLAS optimized),
        # then upcast to float64 for accurate distance computation.
        dot = Xi @ Xj.T
        dot = dot.astype(np.float64)

        # Squared distances using ||a||^2 + ||b||^2 - 2*a.b
        d2 = normsq[start:stop, None] + normsq[None, start:] - 2.0 * dot

        # Guard against tiny negative values due to floating point error
        np.maximum(d2, 0.0, out=d2)

        # Euclidean distances
        np.sqrt(d2, out=d2)

        total += d2.sum(dtype=np.float64)

    # Double to account for the lower triangular part (diagonal contributes 0)
    total *= 2.0

    print(f"TOTAL:{total:.6f}")

if __name__ == "__main__":
    main()
