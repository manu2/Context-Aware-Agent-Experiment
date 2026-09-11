import numpy as np

def main():
    X = np.load('vectors_secondary.npy')  # shape (8000, 1024), float32
    n = X.shape[0]

    # Precompute squared norms in float64 for numerical stability
    Xd = X.astype(np.float64)
    norms = np.einsum('ij,ij->i', Xd, Xd)  # (n,)

    total = 0.0
    block = 500  # balance memory vs speed

    for start in range(0, n, block):
        end = min(start + block, n)
        Xi = Xd[start:end]                     # (b, d)
        dots = Xi @ Xd.T                        # (b, n)
        d2 = norms[start:end, None] + norms[None, :] - 2.0 * dots
        np.maximum(d2, 0.0, out=d2)             # guard against tiny negatives
        d = np.sqrt(d2)
        total += d.sum(dtype=np.float64)

    print(f"TOTAL:{total}")

if __name__ == '__main__':
    main()
