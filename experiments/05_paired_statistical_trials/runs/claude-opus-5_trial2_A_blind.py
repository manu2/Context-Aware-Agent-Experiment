#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between the rows of
an 8,000 x 1,024 float32 matrix stored in 'vectors.npy'.

    TOTAL = sum_{i=1..N} sum_{j=1..N} ||v_i - v_j||_2
          = 2 * sum_{i<j} ||v_i - v_j||_2      (the diagonal contributes 0)

Only numpy + the standard library are used.

Strategy
--------
Materialising the full 8000 x 8000 distance matrix at once is possible but
wasteful, so we stream over row-blocks and, for each block, only touch the
"upper triangle" part (columns >= block start).  That halves both the flops
and the memory traffic.

For each block we use the Gram-matrix identity

    ||x - y||^2 = ||x||^2 + ||y||^2 - 2 <x, y>

which lets BLAS (dgemm) do all the heavy lifting.  Two numerical safeguards
are applied because that identity is prone to catastrophic cancellation:

  1. the data is mean-centred first (shifting all points by a constant does
     not change any distance, but it makes ||x||^2 as small as possible,
     which minimises the cancellation error), and
  2. all arithmetic/accumulation is done in float64, with tiny negative
     squared distances clamped to 0 before the sqrt.
"""

import os
import sys
import numpy as np


FILENAME = "vectors.npy"
BLOCK = 512          # rows per block; ~32 MB per temporary at N=8000


def main() -> None:
    if not os.path.exists(FILENAME):
        sys.exit(f"error: '{FILENAME}' not found in {os.getcwd()}")

    raw = np.load(FILENAME)
    if raw.ndim != 2:
        sys.exit(f"error: expected a 2-D array, got shape {raw.shape}")

    n, d = raw.shape

    # Work in float64 and mean-centre (distances are translation invariant).
    X = np.asarray(raw, dtype=np.float64)
    del raw
    X -= X.mean(axis=0, keepdims=True)
    X = np.ascontiguousarray(X)

    # Squared norms of every row.
    sq = np.einsum("ij,ij->i", X, X)

    upper_sum = 0.0  # sum over strictly-upper-triangular pairs (i < j)

    for start in range(0, n, BLOCK):
        stop = min(start + BLOCK, n)
        m = stop - start

        A = X[start:stop]        # (m, d)
        B = X[start:]            # (n - start, d)  -> only columns j >= start

        # Squared distances between block rows and all rows with index >= start
        G = A @ B.T                                   # (m, n-start)
        G *= -2.0
        G += sq[start:stop, None]
        G += sq[None, start:]
        np.maximum(G, 0.0, out=G)                     # kill tiny negatives
        np.sqrt(G, out=G)                             # now G holds distances

        # Diagonal block (columns 0..m-1 correspond to rows start..stop-1):
        # keep only the strictly upper part (col > row).
        if m > 1:
            upper_sum += float(np.triu(G[:, :m], k=1).sum(dtype=np.float64))
        # Everything to the right of the diagonal block is fully off-diagonal.
        if G.shape[1] > m:
            upper_sum += float(G[:, m:].sum(dtype=np.float64))

        del G

    total = 2.0 * upper_sum  # ordered pairs (i, j), diagonal = 0

    print(f"TOTAL_DIST:{total:.6f}")


if __name__ == "__main__":
    main()