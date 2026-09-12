import os
# Limit BLAS thread usage to match the 1-core CPU quota, reducing thread
# contention overhead.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np


def main():
    X = np.load("vectors_secondary.npy")
    if X.dtype != np.float32:
        X = X.astype(np.float32)

    n = X.shape[0]

    # Precompute squared norms once (float32, matches matmul precision).
    norms = np.einsum("ij,ij->i", X, X, dtype=np.float32)

    chunk_size = 1000
    total_upper = 0.0  # sum over strictly i<j pairs (float64 accumulation)

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        m = end - start

        Xi = X[start:end]        # m x d
        Xj = X[start:]           # (n-start) x d  (includes Xi itself)

        # dot[i_local, j_local] = Xi[i_local] . Xj[j_local]
        dot = Xi @ Xj.T          # m x (n-start), float32

        ni = norms[start:end]
        nj = norms[start:]

        d2 = ni[:, None] + nj[None, :] - 2.0 * dot
        np.maximum(d2, 0, out=d2)
        d = np.sqrt(d2, dtype=np.float32)

        # First m columns correspond to the same index range as Xi rows,
        # need strictly upper triangular part (j_local > i_local).
        tri_part = d[:, :m]
        iu = np.triu_indices(m, k=1)
        if iu[0].size > 0:
            total_upper += tri_part[iu].sum(dtype=np.float64)

        # Remaining columns (beyond m) are all indices greater than any
        # index in this chunk, so they are all valid i<j pairs.
        if d.shape[1] > m:
            total_upper += d[:, m:].sum(dtype=np.float64)

    total = 2.0 * total_upper  # account for both (i,j) and (j,i); diagonal is 0

    print(f"TOTAL:{total:.6f}")


if __name__ == "__main__":
    main()
