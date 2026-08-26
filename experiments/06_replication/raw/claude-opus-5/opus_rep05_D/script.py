#!/usr/bin/env python3
"""
Sum of all pairwise Euclidean distances (ordered pairs, i.e. 2 * sum_{i<j})
for an 8000 x 1024 float32 matrix, under 128 MB RAM / 10 s.

Only numpy + stdlib.
"""

import numpy as np

FILENAME = "vectors.npy"
BLOCK = 256          # rows per block: 256 * 8000 * 4B = 8.2 MB working buffer


def main():
    X = np.load(FILENAME)
    if X.dtype != np.float32:
        X = X.astype(np.float32, copy=False)
    X = np.ascontiguousarray(X)                     # ~32 MB
    n = X.shape[0]

    # Center the data: distances are unchanged, but ||v||^2 and dot products
    # shrink a lot -> much less float32 cancellation error in the Gram trick.
    mu = X.mean(axis=0, dtype=np.float64).astype(np.float32)
    X -= mu

    # Squared row norms (accumulated in float64, stored as float32 for in-place adds)
    sq = np.einsum('ij,ij->i', X, X, dtype=np.float64).astype(np.float32)

    total_pairs = 0.0   # sum over unordered pairs i < j

    for s in range(0, n, BLOCK):
        e = min(s + BLOCK, n)

        # Gram block: (b x e) float32, only columns [0, e) -> lower triangular half
        G = X[s:e] @ X[:e].T                       # BLAS sgemm

        # squared distances, fully in-place (no large temporaries)
        G *= -2.0
        G += sq[s:e, None]
        G += sq[None, :e]
        np.maximum(G, 0.0, out=G)                  # kill tiny negative round-off
        np.sqrt(G, out=G)

        S = float(np.sum(G, dtype=np.float64))         # all entries of the strip
        W = float(np.sum(G[:, s:e], dtype=np.float64)) # diagonal sub-block (counted twice)

        # strip contributes: cross pairs once + diagonal block pairs once
        total_pairs += (S - W) + 0.5 * W

        del G

    total = 2.0 * total_pairs                      # ordered pairs (i,j), diagonal = 0
    print("TOTAL_DIST:%.6f" % total)


if __name__ == "__main__":
    main()