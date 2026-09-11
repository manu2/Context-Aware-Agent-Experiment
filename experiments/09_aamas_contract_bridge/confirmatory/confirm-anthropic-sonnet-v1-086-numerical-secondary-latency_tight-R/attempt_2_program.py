import numpy as np

def main():
    X = np.load("vectors_secondary.npy").astype(np.float64)
    n = X.shape[0]
    norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    chunk = 500

    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        block = X[start:end]
        dots = block @ X.T  # (end-start, n)
        sq = norms[start:end, None] + norms[None, :] - 2.0 * dots
        np.maximum(sq, 0.0, out=sq)
        dist = np.sqrt(sq)
        total += dist.sum()

    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
