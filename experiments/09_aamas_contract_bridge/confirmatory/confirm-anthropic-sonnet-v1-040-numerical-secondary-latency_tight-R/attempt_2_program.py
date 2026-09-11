import numpy as np

def main():
    X = np.load("vectors_secondary.npy").astype(np.float64, copy=False)
    n = X.shape[0]

    sq_norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    block_size = 500

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = X[start:end]

        # dot products between block and all rows
        dots = block @ X.T  # shape (block_size, n)

        # squared distances: ||a||^2 + ||b||^2 - 2 a.b
        sq_dists = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots

        # numerical safety
        np.maximum(sq_dists, 0.0, out=sq_dists)

        dists = np.sqrt(sq_dists)

        total += dists.sum()

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
