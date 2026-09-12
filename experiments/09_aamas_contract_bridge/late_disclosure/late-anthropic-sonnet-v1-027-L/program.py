import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np

def main():
    X = np.load("vectors_secondary.npy")
    X = np.ascontiguousarray(X, dtype=np.float32)
    n = X.shape[0]

    sq = np.einsum('ij,ij->i', X, X, dtype=np.float32)

    total = 0.0
    block = 400  # tuned for memory/time balance

    Xt = X.T  # (D, n) view, contiguous transpose not needed for dot

    for start in range(0, n, block):
        end = min(start + block, n)
        Xb = X[start:end]  # (b, D)
        # (b, n) = Xb @ X.T
        G = Xb.dot(Xt)
        d2 = sq[start:end, None] + sq[None, :] - 2.0 * G
        np.maximum(d2, 0.0, out=d2)
        np.sqrt(d2, out=d2)
        total += d2.sum(dtype=np.float64)
        del G, d2, Xb

    # total is sum over all ordered pairs (i, j) including diagonal
    # print with full precision decimal
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
