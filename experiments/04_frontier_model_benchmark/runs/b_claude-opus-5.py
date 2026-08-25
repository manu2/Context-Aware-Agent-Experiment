#!/usr/bin/env python3
"""
Compute the total sum of all pairwise Euclidean distances

        TOTAL = sum_{i=1..N} sum_{j=1..N} || v_i - v_j ||_2

for the 8,000 x 1,024 float32 matrix stored in 'vectors.npy'.

Only numpy + the standard library are used.

Memory strategy
---------------
*  The full 8,000 x 8,000 distance matrix is NEVER materialised
   (that alone would be 512 MB in float64).
*  The data is read with mmap and copied once into a float32 array (32 MB).
*  Distances are produced in small (BLOCK x BLOCK) tiles via the Gram trick
      ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b
   Only one tile (BLOCK x BLOCK float64) plus two row-blocks
   (BLOCK x 1024 float64) are alive at any moment -> a few MB.
*  Only the upper triangle is computed (work is halved); the result is
   doubled at the end because the matrix is symmetric with a zero diagonal.

Numerical care
--------------
*  Tiles are accumulated in float64 (BLAS dgemm), not float32.
*  The data is mean-centred first: this does not change any distance but
   shrinks ||a||^2, which removes most of the cancellation error of the
   Gram-matrix identity.
*  Negative values caused by round-off are clamped to 0 before sqrt, and the
   exact-zero diagonal is forced.
*  Tile sums are combined with math.fsum (exactly rounded summation).
"""

import math
import os
import numpy as np

PATH = "vectors.npy"
BLOCK = int(os.environ.get("BLOCK", 512))   # tile size: 512 -> ~2 MB tiles


def main():
    # ---- load lazily (memory-map: no full read into RAM yet) -------------
    Xmm = np.load(PATH, mmap_mode="r")
    if Xmm.ndim != 2:
        raise ValueError("expected a 2-D array in %s" % PATH)
    n, d = Xmm.shape

    # ---- pass 1: streaming mean (float64 accumulator) --------------------
    mean = np.zeros(d, dtype=np.float64)
    for s in range(0, n, BLOCK):
        mean += np.asarray(Xmm[s:s + BLOCK], dtype=np.float64).sum(axis=0)
    mean /= n
    mean32 = mean.astype(np.float32)

    # ---- pass 2: centred float32 copy (32 MB) + float64 squared norms ----
    X = np.empty((n, d), dtype=np.float32)
    sq = np.empty(n, dtype=np.float64)
    for s in range(0, n, BLOCK):
        e = min(n, s + BLOCK)
        blk = np.asarray(Xmm[s:e], dtype=np.float32) - mean32   # small temp
        X[s:e] = blk
        b64 = blk.astype(np.float64)
        sq[s:e] = np.einsum("ij,ij->i", b64, b64)
        del blk, b64
    del Xmm  # release the memory map

    # ---- tiled upper-triangular accumulation ----------------------------
    nb = (n + BLOCK - 1) // BLOCK
    parts = []          # one float per tile, summed exactly at the end

    for bi in range(nb):
        i0, i1 = bi * BLOCK, min(n, (bi + 1) * BLOCK)
        Ai = X[i0:i1].astype(np.float64)      # BLOCK x 1024  (~4 MB)
        ni = sq[i0:i1]

        # --- diagonal tile: symmetric, take half of its total sum ---
        T = Ai @ Ai.T                          # BLOCK x BLOCK (~2 MB)
        T *= -2.0
        T += ni[:, None]
        T += ni[None, :]
        np.maximum(T, 0.0, out=T)
        np.fill_diagonal(T, 0.0)               # exact zeros on the diagonal
        np.sqrt(T, out=T)
        parts.append(0.5 * float(T.sum()))
        del T

        # --- off-diagonal tiles (strict upper triangle) ---
        for bj in range(bi + 1, nb):
            j0, j1 = bj * BLOCK, min(n, (bj + 1) * BLOCK)
            Aj = X[j0:j1].astype(np.float64)
            T = Ai @ Aj.T                      # in-place from here on
            T *= -2.0
            T += ni[:, None]
            T += sq[j0:j1][None, :]
            np.maximum(T, 0.0, out=T)
            np.sqrt(T, out=T)
            parts.append(float(T.sum()))
            del Aj, T

        del Ai

    total = 2.0 * math.fsum(parts)             # symmetry, zero diagonal
    print("TOTAL_DIST:%.6f" % total)


if __name__ == "__main__":
    main()