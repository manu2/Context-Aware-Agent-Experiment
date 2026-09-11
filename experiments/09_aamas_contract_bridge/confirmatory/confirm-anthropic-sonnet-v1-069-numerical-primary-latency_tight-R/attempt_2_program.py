import numpy as np

def main():
    X = np.load('vectors.npy')  # (8000, 1024) float32
    X64 = X.astype(np.float64)
    n = X64.shape[0]
    norms = np.sum(X64 * X64, axis=1)  # (n,)

    total = 0.0
    block = 500
    for start in range(0, n, block):
        end = min(start + block, n)
        chunk = X64[start:end]  # (b, d)
        dots = chunk @ X64.T  # (b, n)
        sq = norms[start:end][:, None] + norms[None, :] - 2.0 * dots
        np.maximum(sq, 0.0, out=sq)
        dist = np.sqrt(sq)
        total += dist.sum()

    print(f"TOTAL:{total:.10f}")

if __name__ == '__main__':
    main()
