import numpy as np

def main():
    X = np.load("vectors_secondary.npy", mmap_mode="r")
    n = X.shape[0]

    # Use float64 for accurate norms and dot products
    X64 = np.asarray(X, dtype=np.float64)

    norms = np.einsum('ij,ij->i', X64, X64)

    total = 0.0
    block = 500  # tune for memory/speed balance

    for start in range(0, n, block):
        end = min(start + block, n)
        A = X64[start:end]  # (b, d)
        # dot products between A and all rows
        dots = A @ X64.T  # (b, n)
        # squared distances: norms[i] + norms[j] - 2*dots
        sq = norms[start:end, None] + norms[None, :] - 2.0 * dots
        np.maximum(sq, 0.0, out=sq)
        dists = np.sqrt(sq)
        total += dists.sum()

    # total is a Python float summed via numpy; format as decimal
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
