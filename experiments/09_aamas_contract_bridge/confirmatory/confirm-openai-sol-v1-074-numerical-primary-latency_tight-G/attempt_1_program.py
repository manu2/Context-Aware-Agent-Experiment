import numpy as np

def main():
    vectors = np.load("vectors.npy", mmap_mode="r", allow_pickle=False)
    n = vectors.shape[0]
    block_size = 512

    squared_norms = np.einsum(
        "ij,ij->i", vectors, vectors, dtype=np.float32, optimize=True
    )

    total = 0.0

    for i0 in range(0, n, block_size):
        i1 = min(i0 + block_size, n)
        xi = vectors[i0:i1]
        ni = squared_norms[i0:i1]

        for j0 in range(i0, n, block_size):
            j1 = min(j0 + block_size, n)
            xj = vectors[j0:j1]
            nj = squared_norms[j0:j1]

            distances = xi @ xj.T
            distances *= -2.0
            distances += ni[:, None]
            distances += nj[None, :]
            np.maximum(distances, 0.0, out=distances)

            if i0 == j0:
                np.fill_diagonal(distances, 0.0)

            np.sqrt(distances, out=distances)
            block_sum = float(np.sum(distances, dtype=np.float64))

            total += block_sum if i0 == j0 else 2.0 * block_sum

    print("TOTAL:" + repr(total))

if __name__ == "__main__":
    main()
