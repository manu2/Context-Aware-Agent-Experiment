import numpy as np

def main():
    X = np.load("vectors_secondary.npy")
    X = X.astype(np.float64, copy=False)
    n = X.shape[0]

    norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    chunk_size = 500  # adjust for memory/performance balance

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        Xi = X[start:end]

        dots = Xi @ X.T  # shape (chunk, n)
        sq_dists = norms[start:end, None] + norms[None, :] - 2.0 * dots
        np.maximum(sq_dists, 0.0, out=sq_dists)
        dists = np.sqrt(sq_dists)

        total += dists.sum()

    # total is a numpy float64 scalar; convert to Python float for printing
    total = float(total)
    print(f"TOTAL:{total!r}")

if __name__ == "__main__":
    main()
