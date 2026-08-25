#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances (i, j over ALL ordered pairs) for an
8000 x 1024 float32 matrix, using only numpy + stdlib, under 128 MB / 10 s.
"""
import numpy as np


def main(path="vectors.npy", block=512):
    # ---- load (single 32.8 MB contiguous float32 copy) -------------------
    X = np.load(path, mmap_mode="r")
    N, D = X.shape
    X = np.array(X, dtype=np.float32, order="C")

    # ---- squared norms, accumulated in float64 for accuracy --------------
    sq64 = np.empty(N, dtype=np.float64)
    for a in range(0, N, block):
        b = min(a + block, N)
        chunk = X[a:b].astype(np.float64)          # <= 4 MB temporary
        sq64[a:b] = np.einsum("ij,ij->i", chunk, chunk)
        del chunk
    sq32 = sq64.astype(np.float32)

    # ---- blocked upper-triangle accumulation ----------------------------
    upper = 0.0                                    # sum over i < j
    for i0 in range(0, N, block):
        i1 = min(i0 + block, N)
        m = i1 - i0

        # Gram tile: rows [i0:i1] vs columns [i0:N]  -> BLAS sgemm
        G = X[i0:i1] @ X[i0:].T                    # (m, N-i0) float32, <=16 MB

        # d^2 = |a|^2 + |b|^2 - 2ab, all in place
        G *= np.float32(-2.0)
        G += sq32[i0:i1, None]
        G += sq32[None, i0:]
        np.maximum(G, 0, out=G)                    # kill tiny negatives
        np.sqrt(G, out=G)

        s_all = np.sum(G, dtype=np.float64)        # whole tile
        s_diag = np.sum(G[:, :m], dtype=np.float64)  # symmetric diagonal block
        # diagonal block contributes only its strict upper half = s_diag / 2
        upper += float(s_all) - 0.5 * float(s_diag)
        del G

    total = 2.0 * upper                            # ordered pairs (i,j)
    print("TOTAL_DIST:%.6f" % total)


if __name__ == "__main__":
    main()