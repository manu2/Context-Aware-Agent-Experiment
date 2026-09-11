import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

def main():
    V = np.load("vectors.npy")
    if V.dtype != np.float32:
        V = V.astype(np.float32)
    N = V.shape[0]

    # Precompute squared norms in double precision for numerical stability
    norms = np.einsum('ij,ij->i', V.astype(np.float64), V.astype(np.float64))

    total_upper = 0.0  # sum over i<j of distances

    block_size = 1000
    for bi in range(0, N, block_size):
        R = V[bi:bi + block_size]           # (r, d) float32
        C = V[bi:]                          # (c, d) float32, c = N - bi
        r = R.shape[0]

        dot = R @ C.T                       # float32, shape (r, c)
        ni = norms[bi:bi + r]
        nj = norms[bi:]

        d2 = ni[:, None] + nj[None, :] - 2.0 * dot.astype(np.float64)
        np.maximum(d2, 0.0, out=d2)
        d = np.sqrt(d2)

        # Split: first r columns correspond to the same block (need strict upper triangle)
        local = d[:, :r]
        iu = np.triu_indices(r, k=1)
        total_upper += local[iu].sum()

        # Remaining columns correspond to rows strictly after this block -> all valid i<j pairs
        if C.shape[0] > r:
            total_upper += d[:, r:].sum()

    total = 2.0 * total_upper

    print(f"TOTAL:{total:.6f}")

if __name__ == "__main__":
    main()
