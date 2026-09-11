import numpy as np

def main():
    X = np.load("vectors_secondary.npy")
    X = X.astype(np.float64, copy=False)
    n = X.shape[0]

    sq_norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    chunk_size = 500  # process rows in chunks to limit memory usage

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        chunk = X[start:end]

        # squared distances: ||a||^2 + ||b||^2 - 2 a.b
        dots = chunk @ X.T
        d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots

        # numerical safety: clamp tiny negative values to zero
        np.maximum(d2, 0.0, out=d2)

        dists = np.sqrt(d2)
        total += dists.sum()

    print(f"TOTAL:{total!r}")

if __name__ == "__main__":
    main()
