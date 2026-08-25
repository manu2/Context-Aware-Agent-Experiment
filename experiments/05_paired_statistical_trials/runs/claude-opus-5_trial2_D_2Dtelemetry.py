#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances  sum_{i,j} ||v_i - v_j||_2
for an 8000 x 1024 float32 matrix stored in 'vectors.npy'.

Memory-bounded (<128 MB) and fast (<10 s): blocked upper-triangular
Gram-matrix formulation, numpy/BLAS only.
"""

import numpy as np

FILENAME = "vectors.npy"
BLOCK = 512  # rows per block: 512 * 8000 * 4 B = 16 MB per temp block


def main():
    # ---- load (32 MB for 8000x1024 float32) -------------------------------
    X = np.load(FILENAME)
    if X.ndim != 2:
        raise ValueError("expected a 2-D array")
    if X.dtype != np.float32:
        X = X.astype(np.float32, copy=False)
    X = np.ascontiguousarray(X)
    n, d = X.shape

    if n < 2:
        print("TOTAL_DIST:0.000000")
        return

    # ---- center in place: distances unchanged, cancellation error reduced --
    mu = X.mean(axis=0, dtype=np.float64).astype(np.float32)
    X -= mu

    # squared norms (float64 for accuracy, float32 copy for cheap broadcasting)
    sq64 = np.einsum("ij,ij->i", X, X, dtype=np.float64)
    sq32 = sq64.astype(np.float32)

    total = 0.0
    minus_two = np.float32(-2.0)

    # ---- blocked upper triangle -------------------------------------------
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        b = e - s

        # G[i, k] = <x_{s+i}, x_{s+k}>   (columns cover global indices s..n-1)
        G = np.dot(X[s:e], X[s:].T)          # (b, n-s) float32, BLAS sgemm

        # squared distances, fully in place (no big temporaries)
        np.multiply(G, minus_two, out=G)
        G += sq32[s:]                        # broadcast over columns
        G += sq32[s:e, None]                 # broadcast over rows
        np.maximum(G, 0, out=G)              # kill negative round-off
        np.sqrt(G, out=G)

        # exact zeros on the true diagonal (avoids sqrt(round-off) bias)
        idx = np.arange(b)
        G[idx, idx] = 0.0

        # diagonal block holds both (i,j) and (j,i) already;
        # off-diagonal part is counted once here -> weight 2
        diag_sum = G[:, :b].sum(dtype=np.float64)
        off_sum = G[:, b:].sum(dtype=np.float64) if e < n else 0.0
        total += diag_sum + 2.0 * off_sum

        del G

    print("TOTAL_DIST:{:.6f}".format(total))


if __name__ == "__main__":
    main()