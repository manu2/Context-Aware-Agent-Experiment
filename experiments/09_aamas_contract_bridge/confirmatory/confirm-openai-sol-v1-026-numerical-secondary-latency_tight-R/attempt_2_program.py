import math
import numpy as np


def main() -> None:
    vectors = np.load("vectors_secondary.npy", allow_pickle=False)
    if vectors.shape != (8000, 1024) or vectors.dtype != np.float32:
        raise ValueError("Unexpected input array")

    vectors = np.ascontiguousarray(vectors)
    norms = np.einsum("ij,ij->i", vectors, vectors, dtype=np.float32)

    block_size = 256
    partials = []

    for i in range(0, vectors.shape[0], block_size):
        a = vectors[i:i + block_size]
        na = norms[i:i + block_size]

        for j in range(i, vectors.shape[0], block_size):
            b = vectors[j:j + block_size]
            nb = norms[j:j + block_size]

            distances = np.matmul(a, b.T)
            np.multiply(distances, np.float32(-2.0), out=distances)
            np.add(distances, na[:, None], out=distances)
            np.add(distances, nb[None, :], out=distances)
            np.maximum(distances, np.float32(0.0), out=distances)
            np.sqrt(distances, out=distances)

            if i == j:
                np.fill_diagonal(distances, np.float32(0.0))
                partials.append(float(np.sum(distances, dtype=np.float64)))
            else:
                partials.append(
                    2.0 * float(np.sum(distances, dtype=np.float64))
                )

    total = math.fsum(partials)
    print("TOTAL:" + repr(total))


if __name__ == "__main__":
    main()
