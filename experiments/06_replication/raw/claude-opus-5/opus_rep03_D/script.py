#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances for an 8000 x 1024 float32 matrix.

Strategy
--------
sum_{i,j} ||v_i - v_j|| = 2 * sum_{i<j} ||v_i - v_j||

We never materialize the full 8000x8000 distance matrix (256 MB).
Instead we stream over row-blocks and, for each block, only compute the
part of the Gram matrix belonging to the upper triangle (j >= i), which
also halves the FLOP count.

||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 <v_i, v_j>

The Gram block is produced by a single BLAS sgemm call (fast, multithreaded)
and is then transformed *in place* into distances, so peak extra memory is
one block only.

Numerical note: distances are translation invariant, so the data is centered
first.  This makes ||v_i||^2 + ||v_j||^2 and 2<v_i,v_j> comparable in size and
removes the catastrophic cancellation that the expanded formula would suffer
for non-zero-mean data.  Reductions are accumulated in float64.

Memory budget: X (32.8 MB) + one block (512 x 8000 float32 = 16.4 MB) ~ 50 MB.
"""

import numpy as np


def main():
    X = np.load('vectors.npy')
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    X = np.ascontiguousarray(X)
    n, d = X.shape

    # --- center (distances unchanged, big win for float32 accuracy) ---
    mu = X.mean(axis=0, dtype=np.float64).astype(np.float32)
    X -= mu

    # --- squared norms, computed chunk-wise with float64 accumulation ---
    sq = np.empty(n, dtype=np.float64)
    for a in range(0, n, 1024):
        b = min(a + 1024, n)
        Xc = X[a:b]
        sq[a:b] = np.einsum('ij,ij->i', Xc, Xc, dtype=np.float64)
    sq32 = sq.astype(np.float32)

    B = 512                      # row-block size (tuned for RAM vs BLAS efficiency)
    upper = 0.0                  # sum over strictly upper-triangular pairs

    for a in range(0, n, B):
        b = min(a + B, n)
        m = b - a

        # Gram block against columns [a, n)  -> only the upper triangle region
        G = X[a:b] @ X[a:].T                     # (m, n-a) float32, one sgemm

        # in-place: G <- sqrt(max(sq_i + sq_j - 2G, 0))
        G *= np.float32(-2.0)
        G += sq32[a:b, None]
        G += sq32[None, a:]
        np.maximum(G, 0, out=G)
        np.sqrt(G, out=G)

        # diagonal sub-block: keep only strictly upper part (j > i)
        upper += float(np.sum(np.triu(G[:, :m], 1), dtype=np.float64))
        # everything to the right of the diagonal block is entirely j > i
        if b < n:
            upper += float(np.sum(G[:, m:], dtype=np.float64))

        del G

    total = 2.0 * upper
    print('TOTAL_DIST:%.6f' % total)


if __name__ == '__main__':
    main()