import numpy as np

def main():
    X = np.load("vectors_secondary.npy")
    X = X.astype(np.float64, copy=False)
    n = X.shape[0]

    sq_norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    block_size = 500

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = X[start:end]

        # squared distances: ||a||^2 + ||b||^2 - 2 a.b
        dots = block @ X.T  # shape (block, n)
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots

        # numerical safety: clip small negative values due to floating point errors
        np.maximum(d2, 0.0, out=d2)

        d = np.sqrt(d2)
        total += d.sum()

    # Print with high precision decimal representation
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
