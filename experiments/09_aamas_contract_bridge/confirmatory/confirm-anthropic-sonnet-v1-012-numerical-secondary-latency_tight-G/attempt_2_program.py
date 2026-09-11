import numpy as np

def main():
    X = np.load('vectors_secondary.npy')  # (8000, 1024) float32
    n = X.shape[0]

    # Work in float64 for numerical accuracy in the distance computation.
    Xf = X.astype(np.float64, copy=False)

    # Squared norms of each row.
    norms = np.einsum('ij,ij->i', Xf, Xf)

    total = 0.0
    block = 1000  # tune for memory/time balance

    Xt = Xf.T  # view, no copy

    for start in range(0, n, block):
        end = min(start + block, n)
        Xb = Xf[start:end]                  # (b, d)
        dots = Xb @ Xt                      # (b, n) via BLAS, fast
        dist_sq = norms[start:end, None] + norms[None, :] - 2.0 * dots
        np.maximum(dist_sq, 0.0, out=dist_sq)  # guard against tiny negative values
        np.sqrt(dist_sq, out=dist_sq)
        total += dist_sq.sum()

    # Print as an exact-looking decimal value (the sum itself is a float).
    print(f"TOTAL:{total!r}")

if __name__ == '__main__':
    main()
