#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances for an 8000 x 1024 float32 matrix.

Strategy
--------
The full 8000 x 8000 distance matrix would need 256 MB (float32), which blows the
128 MB budget, so we stream over *row blocks* and never materialize it.

For a block of rows [a:b) we only multiply against columns [a:n) -- i.e. we walk
the upper triangle only, halving the GEMM work (~65 GFLOP instead of ~131).

Distances come from the expansion  ||u-v||^2 = ||u||^2 + ||v||^2 - 2*u.v,
so the heavy lifting is a single BLAS sgemm per block (multi-threaded, fast).

Bookkeeping for one strip S = sum_{i in [a,b), j in [a,n)} d(i,j):
  * the square sub-block [a,b) x [a,b) is symmetric with a zero diagonal, so it
    counts every intra-block pair twice;
  * everything to the right of it counts each pair once.
  => contribution to the strict upper triangle is  S - 0.5 * (sub-block sum).
Final answer = 2 * (strict upper triangle sum), since the requested sum runs over
all ordered pairs i,j (the i == j terms are zero).

Peak RSS: 32 MB (matrix) + 16 MB (block buffer) + interpreter ~= 60 MB.
"""

import numpy as np


def main():
    # mmap first so np.load doesn't transiently hold two copies
    Xm = np.load('vectors.npy', mmap_mode='r')
    X = np.ascontiguousarray(Xm, dtype=np.float32)   # 8000*1024*4 = 32.8 MB
    del Xm

    n = X.shape[0]

    # Row norms without a 32 MB temporary (einsum accumulates in place)
    sq = np.einsum('ij,ij->i', X, X).astype(np.float32)

    B = 512                      # 512 x 8000 float32 buffer = 16.4 MB
    upper = 0.0                  # accumulate in Python float (C double)

    for a in range(0, n, B):
        b = min(a + B, n)
        m = b - a

        # G = Xb @ X[a:].T  -> (m, n-a) float32, one sgemm call
        G = X[a:b] @ X[a:].T

        # G <- sqrt(sq_i + sq_j - 2*G), all in place, no big temporaries
        G *= np.float32(-2.0)
        G += sq[a:b, None]
        G += sq[None, a:]
        np.maximum(G, 0, out=G)          # kill tiny negatives from cancellation
        np.sqrt(G, out=G)

        s_all = float(G.sum(dtype=np.float64))
        s_diag = float(G[:, :m].sum(dtype=np.float64))   # square sub-block
        upper += s_all - 0.5 * s_diag

        del G

    total = 2.0 * upper
    print('TOTAL_DIST:%.6f' % total)


if __name__ == '__main__':
    main()