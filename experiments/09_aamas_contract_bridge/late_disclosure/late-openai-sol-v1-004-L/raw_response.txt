import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy", allow_pickle=False)
    norms = np.einsum("ij,ij->i", vectors, vectors, optimize=False)

    n = vectors.shape[0]
    major_block = 1024
    minor_block = 256
    total = 0.0

    def distance_sum(a, b, na, nb, same_block):
        gram = a @ b.T
        gram *= -2.0
        gram += na[:, None]
        gram += nb[None, :]
        np.maximum(gram, 0.0, out=gram)
        np.sqrt(gram, out=gram)
        if same_block:
            np.fill_diagonal(gram, 0.0)
        return float(np.sum(gram, dtype=np.float64))

    for i0 in range(0, n, major_block):
        i1 = min(i0 + major_block, n)
        xi = vectors[i0:i1]
        ni = norms[i0:i1]

        for j0 in range(i1, n, major_block):
            j1 = min(j0 + major_block, n)
            block_sum = distance_sum(
                xi, vectors[j0:j1], ni, norms[j0:j1], False
            )
            total += 2.0 * block_sum

        for p0 in range(i0, i1, minor_block):
            p1 = min(p0 + minor_block, i1)
            xp = vectors[p0:p1]
            np_ = norms[p0:p1]

            total += distance_sum(xp, xp, np_, np_, True)

            for q0 in range(p1, i1, minor_block):
                q1 = min(q0 + minor_block, i1)
                block_sum = distance_sum(
                    xp, vectors[q0:q1], np_, norms[q0:q1], False
                )
                total += 2.0 * block_sum

    print("TOTAL:" + str(total))


if __name__ == "__main__":
    main()
