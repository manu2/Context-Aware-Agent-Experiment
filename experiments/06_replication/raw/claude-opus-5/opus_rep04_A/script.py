#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between the rows of
an (N x D) matrix stored in 'vectors.npy':

        TOTAL = sum_{i=1..N} sum_{j=1..N} || v_i - v_j ||_2

Only numpy + the standard library are used.

Strategy
--------
A brute-force O(N^2 * D) loop over explicit differences would be ~65 GFLOP of
non-BLAS work for N=8000, D=1024 (very slow).  Instead we use the Gram-matrix
identity

        ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a.b

so each block of distances comes from a single BLAS matmul.

Numerical / memory care:
  * The full 8000x8000 distance matrix (~512 MB in float64) is never
    materialised; rows are processed in blocks.
  * Only the strict upper triangle (i < j) is computed -> half the FLOPs;
    the result is doubled at the end (diagonal terms are exactly 0).
  * Data is promoted to float64 and mean-centred first.  Centring does not
    change any distance but greatly reduces catastrophic cancellation in
    ||a||^2 + ||b||^2 - 2a.b when the data has a large common offset.
  * Tiny negative values from round-off are clamped to 0 before sqrt.
  * Block partial sums are combined with math.fsum (exact summation).
"""

import math
import os
import sys
import time

import numpy as np

FILENAME = "vectors.npy"
TARGET_BLOCK_BYTES = 256 * 1024 * 1024  # ~256 MB working block for the distances


def choose_chunk(n: int, min_chunk: int = 64, max_chunk: int = 1024) -> int:
    """Pick a row-block size so that one (chunk x n) float64 block stays modest."""
    if n == 0:
        return min_chunk
    chunk = max(1, TARGET_BLOCK_BYTES // (8 * n))
    return int(max(min_chunk, min(max_chunk, chunk, n)))


def total_pairwise_distance(X: np.ndarray, chunk: int | None = None,
                            verbose: bool = True) -> float:
    """Sum over ALL ordered pairs (i, j) of ||X[i] - X[j]||_2."""
    n, d = X.shape
    if n < 2:
        return 0.0

    # float64 working copy, mean-centred for numerical stability.
    Xc = np.ascontiguousarray(X, dtype=np.float64)
    Xc -= Xc.mean(axis=0, keepdims=True)

    # Squared norms of every row.
    sq = np.einsum("ij,ij->i", Xc, Xc)

    if chunk is None:
        chunk = choose_chunk(n)

    partials = []
    t0 = time.time()
    for i0 in range(0, n, chunk):
        i1 = min(i0 + chunk, n)
        A = Xc[i0:i1]        # (m x d)   block of "left" rows
        B = Xc[i0:]          # (r x d)   all rows with global index >= i0

        # Squared distances between block rows and every row j >= i0.
        D2 = A @ B.T                       # (m x r) BLAS matmul
        D2 *= -2.0
        D2 += sq[i0:i1, None]
        D2 += sq[None, i0:]

        np.maximum(D2, 0.0, out=D2)        # kill round-off negatives
        D = np.sqrt(D2, out=D2)            # in-place sqrt -> distances

        # Keep only strictly-upper-triangular entries (global j > i):
        # for local row r, that is columns r+1 .. end.
        block_sum = 0.0
        for r in range(i1 - i0):
            block_sum += float(D[r, r + 1:].sum())
        partials.append(block_sum)

        if verbose:
            done = i1 / n
            sys.stderr.write(
                f"\r  rows {i1}/{n} ({100 * done:5.1f}%)  "
                f"elapsed {time.time() - t0:6.1f}s"
            )
            sys.stderr.flush()

    if verbose:
        sys.stderr.write("\n")

    upper_sum = math.fsum(partials)        # sum over i < j
    return 2.0 * upper_sum                 # ordered pairs; diagonal contributes 0


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else FILENAME
    if not os.path.exists(path):
        sys.stderr.write(f"ERROR: file not found: {path}\n")
        return 1

    X = np.load(path)
    if X.ndim != 2:
        sys.stderr.write(f"ERROR: expected a 2-D array, got shape {X.shape}\n")
        return 1
    if not np.isfinite(X).all():
        sys.stderr.write("ERROR: input contains NaN or Inf values\n")
        return 1

    n, d = X.shape
    sys.stderr.write(f"Loaded {path}: shape={X.shape}, dtype={X.dtype}\n")
    sys.stderr.write(f"Pairs (ordered, incl. i==j): {n * n}\n")

    total = total_pairwise_distance(X)

    print(f"TOTAL_DIST:{total:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())