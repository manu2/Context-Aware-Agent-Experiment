#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between the rows of
an (N x D) float32 matrix stored in 'vectors.npy'.

    TOTAL = sum_{i=1..N} sum_{j=1..N} ||v_i - v_j||_2      (ordered pairs, diagonal = 0)

Only numpy + the standard library are used.

Method
------
Naively this is N^2 * D = 8000^2 * 1024 ~ 6.6e10 flops if done row-by-row in
Python -- far too slow.  Instead we use the Gram-matrix identity

    ||a - b||^2 = ||a||^2 + ||b||^2 - 2 <a, b>

so that a whole block of the distance matrix comes from one BLAS GEMM call.
The matrix is processed in blocks so that peak memory stays small, and only the
upper block-triangle is computed (the matrix is symmetric), halving the work.

Numerical care
--------------
* All arithmetic is done in float64.
* The data is mean-centered first (distances are translation invariant).  This
  shrinks ||a||^2 and ||b||^2 and therefore greatly reduces the catastrophic
  cancellation that the Gram identity can suffer from.
* Tiny negative squared distances (round-off) are clipped to 0, and the exact
  diagonal of the diagonal blocks is forced to 0.
* Block sums are accumulated with math.fsum over per-block float64 sums, so the
  final accumulation is exact.
"""

import math
import os
import sys

import numpy as np

FILENAME = sys.argv[1] if len(sys.argv) > 1 else "vectors.npy"
BLOCK = 1024  # rows per block; 1024 x 8000 float64 block ~ 65 MB


def total_pairwise_distance(X: np.ndarray, block: int = BLOCK) -> float:
    """Sum of ||x_i - x_j|| over all ordered pairs (i, j)."""
    n = X.shape[0]

    # float64 + mean-centering (distances are unchanged by translation)
    X = np.asarray(X, dtype=np.float64)
    X = X - X.mean(axis=0, keepdims=True)
    X = np.ascontiguousarray(X)

    sq = np.einsum("ij,ij->i", X, X)  # squared norms

    partials = []
    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        Xi = X[i0:i1]
        sqi = sq[i0:i1][:, None]

        for j0 in range(i0, n, block):           # upper block-triangle only
            j1 = min(j0 + block, n)

            # squared distances for this block: |a|^2 + |b|^2 - 2 a.b
            d2 = Xi @ X[j0:j1].T
            d2 *= -2.0
            d2 += sqi
            d2 += sq[j0:j1][None, :]
            np.maximum(d2, 0.0, out=d2)          # kill round-off negatives
            d = np.sqrt(d2, out=d2)

            if i0 == j0:                          # diagonal block
                np.fill_diagonal(d, 0.0)          # exact zeros on the diagonal
                partials.append(float(d.sum()))   # already counts both triangles
            else:
                partials.append(2.0 * float(d.sum()))  # mirror block (j, i)

    return math.fsum(partials)


def _self_test():
    """Verify the fast routine against a brute-force computation on small data."""
    rng = np.random.default_rng(0)
    A = rng.standard_normal((120, 17)).astype(np.float32)
    fast = total_pairwise_distance(A, block=32)
    slow = math.fsum(
        float(np.linalg.norm(A[i].astype(np.float64) - A[j].astype(np.float64)))
        for i in range(A.shape[0])
        for j in range(A.shape[0])
    )
    assert abs(fast - slow) <= 1e-7 * max(1.0, abs(slow)), (fast, slow)


def main():
    if os.environ.get("SELFTEST"):
        _self_test()
        print("self-test OK", file=sys.stderr)

    X = np.load(FILENAME, mmap_mode="r")
    X = np.asarray(X)
    if X.ndim != 2:
        raise ValueError(f"expected a 2-D array, got shape {X.shape}")

    total = total_pairwise_distance(X)

    print(f"TOTAL_DIST:{total:.6f}")
    # Sum over unordered pairs i < j, in case that is what is wanted:
    print(f"# unordered (i<j) half-sum: {total / 2.0:.6f}", file=sys.stderr)


if __name__ == "__main__":
    main()