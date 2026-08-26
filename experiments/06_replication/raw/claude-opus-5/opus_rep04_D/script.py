#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances for an 8000 x 1024 float32 matrix.

Strategy
--------
* The full 8000x8000 distance matrix would need 256 MB (float32) / 512 MB
  (float64), so it is never materialised.  Instead we stream over row-blocks.
* Distances come from the Gram-matrix identity
      ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b
  where the a.b part is a single BLAS sgemm call (fast, multithreaded).
* Only the upper triangle is computed (block i vs. rows >= block start),
  halving the ~131 GFLOP of work to ~65 GFLOP.
* Squared norms and all accumulations are done in float64 to keep the
  final sum accurate; only the big matrix product stays in float32.

Peak RAM: 32 MB (data) + ~12 MB (per-block buffers) + interpreter ≈ 60 MB.
"""

import numpy as np


def main():
    X = np.load('vectors.npy')
    if X.dtype != np.float32:
        X = X.astype(np.float32)
    X = np.ascontiguousarray(X)                # ensure BLAS-friendly layout
    n = X.shape[0]

    # ---- squared norms in float64, computed in small chunks ----------------
    sq = np.empty(n, dtype=np.float64)
    for s in range(0, n, 512):
        e = min(s + 512, n)
        blk = X[s:e].astype(np.float64)        # <= 4 MB temporary
        sq[s:e] = np.einsum('ij,ij->i', blk, blk)
    del blk

    # ---- blocked upper-triangle accumulation ------------------------------
    B = 128                                    # rows per block
    upper = 0.0                                # sum over unordered pairs i<j

    for s in range(0, n, B):
        e = min(s + B, n)

        # (b x (n-s)) Gram block via sgemm: X[s:e] . X[s:]^T
        G = X[s:e] @ X[s:].T                   # float32, <= 4 MB

        D = G.astype(np.float64)               # <= 8 MB
        del G
        D *= -2.0
        D += sq[s:e, None]
        D += sq[None, s:]
        np.maximum(D, 0.0, out=D)              # kill tiny negative round-off
        np.sqrt(D, out=D)

        # D covers i in [s,e), j in [s,n):
        #   - the leading (b x b) square counts intra-block pairs twice
        #   - the rest counts each cross pair exactly once
        within = D[:, :e - s].sum(dtype=np.float64)
        upper += D.sum(dtype=np.float64) - 0.5 * within
        del D

    total = 2.0 * upper                        # sum over ordered pairs (i,j)
    print('TOTAL_DIST:%.6f' % total)


if __name__ == '__main__':
    main()