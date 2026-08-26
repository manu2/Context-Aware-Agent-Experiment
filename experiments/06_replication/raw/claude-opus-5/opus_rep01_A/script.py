#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between rows of
'vectors.npy'  ->  sum_{i,j} ||v_i - v_j||_2   (ordered pairs, diagonal = 0).

Only numpy + the standard library are used.
"""

import math
import os
import sys

import numpy as np

FILENAME = "vectors.npy"
BLOCK = 512            # rows per block (memory/speed tradeoff)
REL_TOL = 1e-10        # below this, recompute a distance exactly
REFINE_CHUNK = 200_000 # pairs refined per vectorized batch


def refine_small(A, Bm, d2, rows, cols):
    """Recompute selected squared distances exactly (no cancellation)."""
    n_pairs = rows.size
    for s in range(0, n_pairs, REFINE_CHUNK):
        r = rows[s:s + REFINE_CHUNK]
        c = cols[s:s + REFINE_CHUNK]
        diff = A[r] - Bm[c]                       # explicit differences
        d2[r, c] = np.einsum('ij,ij->i', diff, diff)


def main():
    if not os.path.exists(FILENAME):
        sys.exit("error: %s not found" % FILENAME)

    X = np.load(FILENAME)
    if X.ndim != 2:
        sys.exit("error: expected a 2-D matrix, got shape %r" % (X.shape,))

    # float64 accumulation for accuracy; centering shrinks the norms and
    # therefore the cancellation error of the Gram identity (distances are
    # invariant under translation).
    X = np.ascontiguousarray(X, dtype=np.float64)
    X -= X.mean(axis=0)

    n = X.shape[0]
    sq = np.einsum('ij,ij->i', X, X)      # squared norms

    partials = []
    for i0 in range(0, n, BLOCK):
        i1 = min(i0 + BLOCK, n)
        b = i1 - i0

        A = X[i0:i1]        # (b, d)
        Bm = X[i0:]         # (m, d)  -- only columns j >= i0 (upper triangle)
        sq_a = sq[i0:i1]
        sq_b = sq[i0:]

        # ||a||^2 + ||b||^2 - 2 a.b   via one BLAS dgemm
        d2 = A @ Bm.T
        d2 *= -2.0
        d2 += sq_a[:, None]
        d2 += sq_b[None, :]
        np.maximum(d2, 0.0, out=d2)       # kill tiny negative round-off

        # Fix pairs where cancellation destroyed the significant digits.
        scale = sq_a[:, None] + sq_b[None, :]
        rows, cols = np.nonzero(d2 < REL_TOL * scale)
        if rows.size:
            refine_small(A, Bm, d2, rows, cols)
            np.maximum(d2, 0.0, out=d2)
        del scale

        D = np.sqrt(d2, out=d2)

        # The first b columns form this block's diagonal square: keep only
        # its strict upper triangle so every unordered pair is counted once.
        D[:, :b] = np.triu(D[:, :b], k=1)

        partials.append(float(D.sum()))   # numpy pairwise summation per block

    total = 2.0 * math.fsum(partials)     # ordered pairs = 2 x upper triangle

    print("TOTAL_DIST:%.6f" % total)


if __name__ == "__main__":
    main()