import numpy as np

def main():
    X = np.load("vectors_secondary.npy", mmap_mode="r")
    n = X.shape[0]
    X = np.asarray(X, dtype=np.float64)

    norms = np.einsum('ij,ij->i', X, X)

    block = 500
    total = 0.0

    for start in range(0, n, block):
        end = min(start + block, n)
        Xi = X[start:end]
        dots = Xi @ X.T
        d2 = norms[start:end, None] + norms[None, :] - 2.0 * dots
        np.maximum(d2, 0.0, out=d2)
        d = np.sqrt(d2)
        total += d.sum()

    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
