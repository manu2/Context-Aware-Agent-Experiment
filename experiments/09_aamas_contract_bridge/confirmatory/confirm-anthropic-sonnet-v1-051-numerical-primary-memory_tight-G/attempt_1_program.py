import numpy as np

def main():
    X = np.load('vectors.npy')
    X = X.astype(np.float64, copy=False)
    N = X.shape[0]

    # squared norms of each row
    sq = np.einsum('ij,ij->i', X, X)

    total = 0.0
    block = 500  # balance between memory and speed

    Xt = X.T  # reuse transpose view

    for start in range(0, N, block):
        end = min(start + block, N)
        Xi = X[start:end]
        dots = Xi @ Xt  # shape (b, N)
        d2 = sq[start:end, None] + sq[None, :] - 2.0 * dots
        np.maximum(d2, 0.0, out=d2)  # guard against tiny negative values from fp error
        np.sqrt(d2, out=d2)
        total += d2.sum()

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
