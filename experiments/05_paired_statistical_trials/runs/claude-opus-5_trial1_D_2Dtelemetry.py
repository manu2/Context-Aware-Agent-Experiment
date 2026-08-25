#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances for an 8000 x 1024 float32 matrix.

Strategy
--------
The full 8000x8000 distance matrix would need 256 MB (float32), which blows the
128 MB budget, so the computation is blocked:

    ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a.b

Only the upper block-triangle is evaluated (the matrix is symmetric, diagonal is
zero), off-diagonal blocks are counted twice.  Each block product is a single
BLAS sgemm call (fast, multi-threaded); the elementwise finishing work is done
in-place to avoid temporaries, and the per-block reduction is accumulated in
float64 to keep the final sum accurate.

Memory peak:  matrix (32 MB) + one block buffer (16 MB) + slack  ~ 55 MB.
Only numpy + stdlib are used.
"""

import os

# Make sure BLAS uses all available cores (must be set before numpy import).
_nthreads = str(os.cpu_count() or 1)
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, _nthreads)

import numpy as np

FILENAME = "vectors.npy"
BLOCK = 2000          # 2000x2000 float32 block = 16 MB


def main():
    # Load as float32, C-contiguous (32 MB for 8000x1024).
    X = np.load(FILENAME, mmap_mode="r")
    X = np.ascontiguousarray(X, dtype=np.float32)
    n, d = X.shape

    # Squared row norms, accumulated in float64 (block-wise, tiny buffers),
    # then cast to float32 for the block arithmetic.
    norms64 = np.empty(n, dtype=np.float64)
    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)
        norms64[s:e] = np.einsum("ij,ij->i", X[s:e], X[s:e], dtype=np.float64)
    norms = norms64.astype(np.float32)

    total = 0.0
    m2 = np.float32(-2.0)

    for i0 in range(0, n, BLOCK):
        i1 = min(i0 + BLOCK, n)
        A = X[i0:i1]
        na = norms[i0:i1][:, None]          # column vector

        for j0 in range(i0, n, BLOCK):
            j1 = min(j0 + BLOCK, n)
            B = X[j0:j1]
            nb = norms[j0:j1][None, :]      # row vector

            # C = -2 * A @ B.T  (single sgemm), then add the norms in place.
            C = A @ B.T                     # float32, (i1-i0) x (j1-j0)
            C *= m2
            C += na
            C += nb
            np.maximum(C, 0, out=C)         # guard against tiny negatives
            np.sqrt(C, out=C)

            s = float(C.sum(dtype=np.float64))
            total += s if i0 == j0 else 2.0 * s

            del C                           # release the 16 MB block promptly

    print("TOTAL_DIST:{:.6f}".format(total))


if __name__ == "__main__":
    main()