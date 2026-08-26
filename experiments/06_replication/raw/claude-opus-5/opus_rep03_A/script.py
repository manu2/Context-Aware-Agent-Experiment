#!/usr/bin/env python3
"""
pairwise_sum.py

Computes  S = sum_{i,j} ||v_i - v_j||_2   over ALL ordered pairs (i, j)
for the 8,000 x 1,024 float32 matrix stored in 'vectors.npy'.

Only numpy + the Python standard library are used.

Strategy
--------
* 8,000^2 = 64,000,000 pairs -> a full float64 distance matrix would be 512 MB.
  We therefore work in blocks and never materialize the full matrix.
* Distances are obtained from the Gram-matrix identity
      ||a - b||^2 = ||a||^2 + ||b||^2 - 2 a.b
  which lets BLAS (numpy's matmul) do the heavy lifting (~1.3e11 FLOPs total,
  seconds instead of hours compared to a Python loop).
* Numerical care:
    - everything is promoted to float64,
    - the data is mean-centered first (distances are translation invariant);
      this shrinks ||v||^2 and hence the catastrophic cancellation in the
      identity above,
    - squared distances are clipped at 0 before the sqrt,
    - block partial sums are combined with math.fsum (exact accumulation),
    - only the strict upper triangle is summed, then doubled, so the result is
      perfectly symmetric and the zero diagonal is handled exactly.
"""

import math
import os
import sys
import time

import numpy as np

PATH = os.environ.get("VECTORS_PATH", "vectors.npy")
BLOCK = int(os.environ.get("BLOCK", 1024))          # rows per tile
SELFTEST_N = int(os.environ.get("SELFTEST_N", 256))  # 0 disables the check


def load_matrix(path):
    X = np.load(path, mmap_mode="r")
    X = np.ascontiguousarray(X, dtype=np.float64)   # promote once, in RAM (~66 MB)
    if X.ndim != 2:
        raise ValueError(f"expected a 2-D array, got shape {X.shape}")
    return X


def upper_triangle_distance_sum(X, block=BLOCK):
    """Return sum_{i<j} ||x_i - x_j||_2 using blocked Gram-matrix computation."""
    n = X.shape[0]
    sq = np.einsum("ij,ij->i", X, X)                # squared norms, float64
    parts = []                                      # one partial sum per tile

    for i0 in range(0, n, block):
        i1 = min(i0 + block, n)
        Xi, si = X[i0:i1], sq[i0:i1]

        for j0 in range(i0, n, block):              # upper block-triangle only
            j1 = min(j0 + block, n)

            # D2 = |xi|^2 + |xj|^2 - 2 <xi, xj>
            D2 = Xi @ X[j0:j1].T
            D2 *= -2.0
            D2 += si[:, None]
            D2 += sq[j0:j1][None, :]

            np.maximum(D2, 0.0, out=D2)             # kill tiny negative round-off
            D = np.sqrt(D2, out=D2)

            if i0 == j0:                            # diagonal tile: strict upper
                parts.append(float(np.triu(D, 1).sum()))
            else:
                parts.append(float(D.sum()))

    return math.fsum(parts)


def brute_force_upper(X):
    """O(m^2 d) reference using explicit differences (no cancellation trick)."""
    m = X.shape[0]
    total = 0.0
    for i in range(m - 1):
        d = X[i + 1:] - X[i]
        total += float(np.sqrt(np.einsum("ij,ij->i", d, d)).sum())
    return total


def main():
    t0 = time.time()
    X = load_matrix(PATH)
    n, d = X.shape
    print(f"[info] loaded {PATH}: {n} x {d} ({X.dtype})", file=sys.stderr)

    # Translation invariance: centering improves conditioning of the Gram trick.
    X -= X.mean(axis=0, keepdims=True)

    # ---- optional self-test on a small sub-block --------------------------
    if SELFTEST_N > 1:
        m = min(SELFTEST_N, n)
        ref = brute_force_upper(X[:m])
        got = upper_triangle_distance_sum(X[:m], block=64)
        rel = abs(got - ref) / max(ref, 1e-300)
        print(f"[info] self-test on {m} rows: rel. error {rel:.3e}", file=sys.stderr)
        if rel > 1e-9:
            print("[warn] self-test error larger than expected", file=sys.stderr)

    # ---- full computation -------------------------------------------------
    upper = upper_triangle_distance_sum(X, block=BLOCK)
    total = 2.0 * upper          # sum over ALL ordered pairs; diagonal is 0

    print(f"[info] elapsed {time.time() - t0:.1f}s "
          f"({n * (n - 1) // 2:,} unique pairs)", file=sys.stderr)
    print(f"TOTAL_DIST:{total:.6f}")


if __name__ == "__main__":
    main()