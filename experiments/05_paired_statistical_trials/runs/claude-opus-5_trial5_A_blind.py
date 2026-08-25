#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances between the rows
of an 8,000 x 1,024 float32 matrix stored in 'vectors.npy'.

    S = sum_{i=0}^{n-1} sum_{j=0}^{n-1} || v_i - v_j ||_2

(Full double sum: every unordered pair is counted twice, diagonal terms are 0.)

Only numpy + the standard library are used.
"""

import os
import sys
import time
import numpy as np

FILENAME = "vectors.npy"
BLOCK = 512          # rows of the distance matrix computed at a time


def total_pairwise_distance(X, block=BLOCK):
    """
    Sum of ||x_i - x_j|| over the strict upper triangle (i < j), returned
    doubled so that it equals the full double sum over all (i, j).

    Uses the identity  ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b  evaluated in
    float64 with BLAS matrix products, processed in row blocks so that the
    full 8000 x 8000 distance matrix is never materialised.
    """
    n = X.shape[0]

    # Translation invariance: centering the data minimises ||x||^2 and thus
    # greatly reduces catastrophic cancellation in the Gram-matrix identity.
    Xc = X - X.mean(axis=0, dtype=np.float64)
    Xc = np.ascontiguousarray(Xc, dtype=np.float64)

    sq = np.einsum("ij,ij->i", Xc, Xc)          # squared norms, float64

    partials = []                                # keep block sums separate
    for start in range(0, n, block):
        end = min(start + block, n)
        b = end - start

        # Only the columns j >= start are needed (upper triangle).
        G = Xc[start:end] @ Xc[start:].T         # (b, n-start)
        d2 = sq[start:end, None] + sq[None, start:]
        d2 -= 2.0 * G
        np.maximum(d2, 0.0, out=d2)              # kill tiny negative round-off
        np.sqrt(d2, out=d2)                      # now distances

        # Columns beyond this block: all belong to the strict upper triangle.
        s = d2[:, b:].sum(dtype=np.float64)
        # Square diagonal sub-block: take its strict upper triangle only.
        if b > 1:
            s += np.triu(d2[:, :b], 1).sum(dtype=np.float64)
        partials.append(float(s))

        del G, d2

    upper = float(np.sum(np.asarray(partials, dtype=np.float64)))
    return 2.0 * upper


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else FILENAME
    if not os.path.exists(path):
        sys.exit(f"ERROR: '{path}' not found")

    t0 = time.time()
    X = np.load(path, mmap_mode="r")
    X = np.asarray(X)                            # ~31 MB as float32
    if X.ndim != 2:
        sys.exit(f"ERROR: expected a 2-D array, got shape {X.shape}")

    total = total_pairwise_distance(X)

    print(f"TOTAL_DIST:{total:.6f}")
    print(f"# shape={X.shape} dtype={X.dtype} elapsed={time.time()-t0:.2f}s",
          file=sys.stderr)


if __name__ == "__main__":
    main()