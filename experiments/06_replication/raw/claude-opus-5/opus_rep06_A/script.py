#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances for an 8,000 x 1,024 float32 matrix.

Computes  S = sum_{i,j} ||v_i - v_j||_2   (all ordered pairs; diagonal = 0,
so S = 2 * sum_{i<j} ||v_i - v_j||_2).

Only numpy + stdlib are used.  The 8000x8000 distance matrix (512 MB in
float64) is never materialized: it is built and reduced in row blocks.
"""

import math
import sys
import time

import numpy as np

PATH = "vectors.npy"
BLOCK = 512          # rows of the distance matrix per chunk (~33 MB in float64)


def load(path):
    X = np.load(path, mmap_mode="r")          # avoid a double in-RAM copy
    if X.ndim != 2:
        raise ValueError(f"expected a 2-D array, got shape {X.shape}")
    # float64 accumulation: the Gram trick below is numerically delicate in float32
    return np.ascontiguousarray(X, dtype=np.float64)


def total_pairwise_distance(X, block=BLOCK):
    n = X.shape[0]

    # Centering does not change any distance but shrinks ||x||^2 relative to
    # ||x - y||^2, which limits cancellation in  d2 = |x|^2 + |y|^2 - 2 x.y
    X = X - X.mean(axis=0, dtype=np.float64)

    sq = np.einsum("ij,ij->i", X, X)          # squared norms, float64
    Xt = np.ascontiguousarray(X.T)            # one transposed copy for fast GEMM

    partials = []                             # summed with fsum -> no drift
    for s in range(0, n, block):
        e = min(s + block, n)
        D = X[s:e] @ Xt                       # BLAS dgemm: (b, n)
        D *= -2.0
        D += sq[s:e, None]
        D += sq[None, :]
        np.maximum(D, 0.0, out=D)             # kill tiny negative round-off
        np.sqrt(D, out=D)
        # exact zeros on the diagonal (round-off can leave ~1e-6 there)
        rows = np.arange(e - s)
        D[rows, rows + s] = 0.0
        partials.append(float(D.sum(dtype=np.float64)))

    return math.fsum(partials)


def self_check(X, m=200, seed=0):
    """Brute-force check on a random submatrix: exact differences vs. Gram trick."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(X.shape[0], size=min(m, X.shape[0]), replace=False)
    S = np.asarray(X[idx], dtype=np.float64)
    exact = math.fsum(
        float(np.sqrt(np.einsum("ij,ij->i", S - S[i], S - S[i])).sum())
        for i in range(S.shape[0])
    )
    approx = total_pairwise_distance(S, block=64)
    rel = abs(approx - exact) / max(exact, 1e-300)
    print(f"[check] {S.shape[0]}-row subset: exact={exact:.6f} "
          f"blocked={approx:.6f} rel_err={rel:.3e}", file=sys.stderr)


def main():
    t0 = time.time()
    X = load(PATH)
    n, d = X.shape
    print(f"[info] loaded {PATH}: {n} x {d}", file=sys.stderr)

    self_check(X)

    total = total_pairwise_distance(X)

    print(f"[info] ordered pairs (i,j): {total:.6f}", file=sys.stderr)
    print(f"[info] unordered pairs i<j: {total / 2.0:.6f}", file=sys.stderr)
    print(f"[info] elapsed: {time.time() - t0:.1f}s", file=sys.stderr)

    print(f"TOTAL_DIST:{total:.6f}")


if __name__ == "__main__":
    main()