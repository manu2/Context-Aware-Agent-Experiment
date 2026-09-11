import numpy as np

def main():
    vectors = np.load("vectors.npy", allow_pickle=False)
    n = vectors.shape[0]
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    total = 0.0
    block_size = 256

    for start in range(0, n, block_size):
        stop = min(start + block_size, n)
        block = vectors[start:stop]
        block_rows = stop - start

        distances = block @ vectors[start:].T
        distances *= np.float32(-2.0)
        distances += norms[start:stop, None]
        distances += norms[None, start:]
        np.maximum(distances, np.float32(0.0), out=distances)
        np.sqrt(distances, out=distances)

        diagonal = np.arange(block_rows)
        distances[diagonal, diagonal] = np.float32(0.0)

        within = np.sum(distances[:, :block_rows], dtype=np.float64)
        after = np.sum(distances[:, block_rows:], dtype=np.float64)
        total += float(within + 2.0 * after)

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
