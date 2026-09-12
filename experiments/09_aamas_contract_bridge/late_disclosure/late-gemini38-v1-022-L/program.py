import math
import numpy as np


def main():
    # Memory-map the array to keep memory well below the 128 MiB limit
    X = np.load("vectors_secondary.npy", mmap_mode="r")
    N = X.shape[0]

    chunk_size = 1000
    num_chunks = (N + chunk_size - 1) // chunk_size

    # Precompute squared norms in float64
    norms = np.empty(N, dtype=np.float64)
    for i in range(num_chunks):
        start = i * chunk_size
        end = min(N, (i + 1) * chunk_size)
        chunk = X[start:end].astype(np.float64)
        norms[start:end] = np.sum(chunk * chunk, axis=1)

    chunk_sums = []

    for i in range(num_chunks):
        i_start = i * chunk_size
        i_end = min(N, (i + 1) * chunk_size)
        Xi = X[i_start:i_end].astype(np.float64)
        norms_i = norms[i_start:i_end]

        for j in range(i, num_chunks):
            j_start = j * chunk_size
            j_end = min(N, (j + 1) * chunk_size)
            norms_j = norms[j_start:j_end]

            if j == i:
                Xj = Xi
            else:
                Xj = X[j_start:j_end].astype(np.float64)

            # Compute squared distances using matrix multiplication
            G = Xi @ Xj.T
            G *= -2.0
            G += norms_i[:, None]
            G += norms_j[None, :]

            # Clamp precision artifacts and zero diagonal for self-distance
            np.maximum(G, 0.0, out=G)
            if i == j:
                np.fill_diagonal(G, 0.0)

            np.sqrt(G, out=G)

            if i == j:
                chunk_sums.append(float(G.sum()))
            else:
                chunk_sums.append(float(2.0 * G.sum()))

            if j != i:
                del Xj

        del Xi

    total = math.fsum(chunk_sums)
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
