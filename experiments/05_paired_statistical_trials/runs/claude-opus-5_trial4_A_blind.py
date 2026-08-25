#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between rows of a
matrix stored in 'vectors.npy'  ->  sum_{i,j} ||v_i - v_j||_2

Only numpy + the standard library are used.

Strategy
--------
A full 8000 x 8000 distance matrix in float64 is ~512 MB, and the naive
"expand to (n, n, d)" approach would need ~500 GB.  Instead we use the
Gram-matrix identity

        ||a - b||^2 = ||a||^2 + ||b||^2 - 2 <a, b>

evaluated in row-blocks, so only one (block_rows x n) slab lives in memory at
a time and the heavy lifting is a single BLAS GEMM call per block.

Accuracy / robustness notes:
  * The Gram trick is done in float64 (float32 accumulation over 1024 terms
    plus the subtractive cancellation can cost several digits, and blows up
    for near-duplicate rows).
  * Round-off can make d^2 slightly negative -> clipped at 0 before sqrt.
  * Only the strict upper triangle is computed (halves the work); the result
    is doubled at the end since the requested double sum counts each unordered
    pair twice and the diagonal contributes exactly 0.
  * Block partial sums are combined with math.fsum for an exactly-rounded
    final accumulation.
"""

import math
import os
import sys

import numpy as np


def total_pairwise_distance(X: np.ndarray, block: int = 512) -> float:
    """Return sum_{i,j} ||X[i] - X[j]||_2 (ordered pairs, diagonal included)."""
    n = X.shape[0]
    if n < 2:
        return 0.0

    # Work in float64: the squared-norm subtraction is cancellation-prone.
    Xd = np.ascontiguousarray(X, dtype=np.float64)
    sq = np.einsum('ij,ij->i', Xd, Xd)          # squared row norms, float64

    partials = []                                # one entry per block

    for start in range(0, n, block):
        stop = min(start + block, n)
        b = stop - start

        A = Xd[start:stop]                       # (b, d)
        B = Xd[start:]                           # (n-start, d)  -> upper strip

        # Gram matrix via BLAS (this is the only O(n^2 d) work)
        G = A @ B.T                              # (b, n-start)

        # Squared distances: ||a||^2 + ||b||^2 - 2<a,b>
        d2 = sq[start:stop, None] + sq[None, start:]
        d2 -= 2.0 * G
        np.maximum(d2, 0.0, out=d2)              # kill tiny negative round-off
        D = np.sqrt(d2, out=d2)                  # in-place sqrt

        # Keep only strictly-upper-triangular entries (global i < j).
        # Columns [0:b] of the strip form the diagonal square block; everything
        # to the right of it is already entirely in the upper triangle.
        head = D[:, :b]
        s = D.sum() - head.sum() + np.triu(head, 1).sum()
        partials.append(float(s))

        del G, d2, D, head

    # Each unordered pair counted once above; the full double sum counts it
    # twice (diagonal terms are exactly zero).
    return 2.0 * math.fsum(partials)


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else 'vectors.npy'
    if not os.path.exists(path):
        sys.exit(f"error: '{path}' not found")

    X = np.load(path, mmap_mode='r')             # avoid a needless full copy
    X = np.asarray(X)

    if X.ndim != 2:
        sys.exit(f"error: expected a 2-D array, got shape {X.shape}")

    total = total_pairwise_distance(X, block=512)
    print(f"TOTAL_DIST:{total:.6f}")


if __name__ == '__main__':
    main()