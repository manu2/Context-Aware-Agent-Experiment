import numpy as np

def main():
    X = np.load('vectors_secondary.npy')  # shape (8000, 1024), float32
    X = np.ascontiguousarray(X, dtype=np.float32)
    n = X.shape[0]

    # Row squared norms computed with float64 accumulation for better precision
    sq = X * X  # float32 temp, ~32MB
    norms = np.sum(sq, axis=1, dtype=np.float64)  # shape (n,)
    del sq

    total = 0.0
    block = 200  # rows per block to keep memory low

    Xt = X.T  # view, no copy (contiguous transpose not forced)

    for start in range(0, n, block):
        end = min(start + block, n)
        Xi = X[start:end]  # (b, 1024) float32
        dot = Xi @ Xt      # (b, n) float32 matmul (BLAS)
        dot64 = dot.astype(np.float64)
        del dot

        d2 = norms[start:end, None] + norms[None, :] - 2.0 * dot64
        del dot64

        np.maximum(d2, 0.0, out=d2)
        np.sqrt(d2, out=d2)

        total += float(np.sum(d2, dtype=np.float64))
        del d2

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
