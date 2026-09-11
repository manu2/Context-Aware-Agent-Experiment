import numpy as np


def main():
    # Load vectors and convert to float64 to ensure high numerical precision
    v = np.load("vectors.npy").astype(np.float64)
    n = v.shape[0]

    # Precompute squared L2 norms for all vectors
    sq_norms = np.einsum("ij,ij->i", v, v)

    total = 0.0
    chunk_size = 1000

    # Process in row chunks to avoid materializing large intermediate arrays
    for i in range(0, n, chunk_size):
        chunk = v[i : i + chunk_size]
        chunk_len = len(chunk)

        # gram matrix: (chunk_len, n)
        gram = chunk @ v.T

        # Pairwise squared distances: ||x - y||^2 = ||x||^2 + ||y||^2 - 2*(x . y)
        d2 = sq_norms[i : i + chunk_len, None] + sq_norms[None, :] - 2.0 * gram
        np.maximum(d2, 0.0, out=d2)

        # Explicitly ensure the diagonal (distance from vector to itself) is zero
        for r in range(chunk_len):
            d2[r, i + r] = 0.0

        np.sqrt(d2, out=d2)
        total += float(np.sum(d2))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
