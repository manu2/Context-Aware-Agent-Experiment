#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances for an 8000 x 1024 float32 matrix.

Strategy
--------
sum_{i,j} ||v_i - v_j|| = 2 * sum_{i<j} ||v_i - v_j||

The full 8000x8000 distance matrix would need 256 MB (float32) / 512 MB (float64),
so it is never materialized.  Instead we stream over row-blocks and, for each
block, only touch the columns j >= i0 (upper trapezoid) -> half the FLOPs.

Per block we use the Gram-matrix identity
        d^2(i,j) = ||v_i||^2 + ||v_j||^2 - 2 <v_i, v_j>
where the inner products come from a single BLAS sgemm call (fast, multithreaded),
while the accumulation/subtraction/sqrt is done in float64 to avoid cancellation
and summation error.

Peak memory: X (32.8 MB) + G float32 (<=8 MB) + D float64 (<=16 MB) ~= 60 MB.
"""

import numpy as np

FILENAME = "vectors.npy"
ROW_BLOCK = 256          # 256 x 8000 float64 = 16 MB working buffer


def main():
    X = np.load(FILENAME)
    if X.dtype != np.float32:
        X = X.astype(np.float32, copy=False)
    X = np.ascontiguousarray(X)
    n, d = X.shape

    # --- squared norms in float64 (computed block-wise to bound memory) -----
    sq = np.empty(n, dtype=np.float64)
    step = 1024
    for s in range(0, n, step):
        e = min(s + step, n)
        blk = X[s:e].astype(np.float64)          # <= 8 MB
        sq[s:e] = np.einsum('ij,ij->i', blk, blk)
        del blk

    total_upper = 0.0                            # sum over strictly upper pairs

    for i0 in range(0, n, ROW_BLOCK):
        i1 = min(i0 + ROW_BLOCK, n)
        b = i1 - i0

        # Gram block: rows [i0:i1] against all columns [i0:n]  (single sgemm)
        G = X[i0:i1] @ X[i0:].T                  # (b, n-i0) float32

        D = G.astype(np.float64)                 # promote once
        del G
        D *= -2.0
        D += sq[i0:i1, None]                     # ||v_i||^2
        D += sq[i0:][None, :]                    # ||v_j||^2
        np.maximum(D, 0.0, out=D)                # kill tiny negatives
        np.sqrt(D, out=D)

        # Columns [i0:i1] form the symmetric diagonal block: it contains each
        # in-block pair twice (and zeros on the diagonal) -> count it half.
        s_all = float(D.sum())
        s_diag = float(D[:, :b].sum())
        total_upper += s_all - 0.5 * s_diag
        del D

    total = 2.0 * total_upper
    print("TOTAL_DIST:%.6f" % total)


if __name__ == "__main__":
    main()