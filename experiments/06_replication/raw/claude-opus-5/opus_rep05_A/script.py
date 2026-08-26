#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between the rows
of an 8,000 x 1,024 float32 matrix stored in 'vectors.npy'.

    S = sum_{i=1..N} sum_{j=1..N} ||v_i - v_j||_2

Only numpy + the standard library are used.

Strategy
--------
A full N x N distance matrix (8000^2 = 64M doubles = 512 MB) is avoided by
processing the data in row blocks and only touching the strict upper triangle
(i < j), then doubling the result (the diagonal contributes exactly 0).

Distances are obtained from the Gram-matrix identity
    ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a.b
which lets BLAS (numpy's matmul) do the heavy lifting.  Two numerical
safeguards are applied:
  * everything is promoted to float64 and the data is mean-centered first
    (distances are translation invariant, but centering greatly reduces
    catastrophic cancellation in the identity above),
  * tiny negative round-off values are clipped to 0 before the sqrt.
Block sums are combined with math.fsum for an exactly-rounded accumulation.
"""

import math
import os
import sys

import numpy as np

FILENAME = "vectors.npy"
BLOCK = 512          # rows per block; tune for cache/RAM (512 -> ~32 MB temporaries)


def total_pairwise_distance(X: np.ndarray, block: int = BLOCK) -> float:
    """Sum over all ordered pairs (i, j) of ||X[i] - X[j]||_2."""
    n = X.shape[0]
    if n < 2:
        return 0.0

    # float64 working copy, mean-centered for numerical stability.
    X = np.array(X, dtype=np.float64, copy=True)
    X -= X.mean(axis=0, keepdims=True)

    # Squared norms of every row.
    sq = np.einsum("ij,ij->i", X, X)

    partials = []  # per-block sums, combined at the end with fsum

    for start in range(0, n, block):
        end = min(start + block, n)
        A = X[start:end]                     # rows of this block
        m = end - start

        # Distances from this block to all rows with index >= start
        # (upper triangle only -> each unordered pair visited once).
        G = A @ X[start:].T                  # (m, n-start) BLAS GEMM
        d2 = sq[start:end, None] + sq[None, start:] - 2.0 * G
        np.maximum(d2, 0.0, out=d2)          # kill round-off negatives
        d = np.sqrt(d2, out=d2)              # in-place sqrt

        # Diagonal sub-block: keep strictly-upper part only.
        diag_part = d[:, :m]
        partials.append(float(np.triu(diag_part, k=1).sum()))

        # Everything to the right of the diagonal block is fully counted.
        if d.shape[1] > m:
            partials.append(float(d[:, m:].sum()))

    upper_sum = math.fsum(partials)          # sum over i < j
    return 2.0 * upper_sum                   # ordered pairs (i,j) and (j,i)


def main() -> None:
    if not os.path.exists(FILENAME):
        sys.exit(f"error: '{FILENAME}' not found in {os.getcwd()}")

    X = np.load(FILENAME, mmap_mode="r")     # memory-map: avoid a needless copy
    X = np.asarray(X)

    if X.ndim != 2:
        sys.exit(f"error: expected a 2-D array, got shape {X.shape}")

    total = total_pairwise_distance(X)

    print(f"TOTAL_DIST:{total:.6f}")


if __name__ == "__main__":
    main()