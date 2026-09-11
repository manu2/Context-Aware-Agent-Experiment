import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

def main():
    X = np.load("vectors.npy")
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    n = X.shape[0]

    # squared norms in float64 for better numerical stability
    norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)

    total_upper = 0.0  # sum over i<j of dist(i,j)

    chunk_size = 800  # tuned to balance memory and matmul efficiency

    i0 = 0
    while i0 < n:
        i1 = min(i0 + chunk_size, n)
        cs = i1 - i0

        A = X[i0:i1]          # (cs, d) float32
        B = X[i0:]             # (n - i0, d) float32

        # dot products via BLAS (float32 GEMM for speed)
        D = A @ B.T            # (cs, n - i0) float32
        D64 = D.astype(np.float64)

        normsA = norms[i0:i1]              # (cs,)
        normsB = norms[i0:]                # (n - i0,)

        sqd = normsA[:, None] + normsB[None, :] - 2.0 * D64
        np.maximum(sqd, 0.0, out=sqd)
        dist = np.sqrt(sqd)

        # Split into the square block (columns 0..cs-1) needing strict upper
        # triangle, and the rest (columns cs..end) which are all valid (j > i).
        if cs > 1:
            square_block = dist[:, :cs]
            tri = np.triu(square_block, k=1)
            total_upper += tri.sum()
        if dist.shape[1] > cs:
            rest = dist[:, cs:]
            total_upper += rest.sum()

        i0 = i1

    total = 2.0 * total_upper

    print(f"TOTAL:{total:.6f}")

if __name__ == "__main__":
    main()
