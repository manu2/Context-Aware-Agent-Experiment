import numpy as np


def main():
    vectors = np.load("vectors_secondary.npy")
    N = vectors.shape[0]

    # Use float64 for numerical precision and stability
    V = vectors.astype(np.float64)
    norms_sq = np.sum(V**2, axis=1)

    total = 0.0
    batch_size = 1000

    for i in range(0, N, batch_size):
        V_batch = V[i : i + batch_size]
        # Pairwise dot products for the batch against all vectors
        dots = V_batch @ V.T

        # ||x - y||^2 = ||x||^2 + ||y||^2 - 2<x, y>
        d2 = norms_sq[i : i + batch_size, None] + norms_sq[None, :] - 2.0 * dots
        np.maximum(d2, 0.0, out=d2)
        np.sqrt(d2, out=d2)

        # Ensure diagonal entries are exactly zero
        for r in range(len(V_batch)):
            d2[r, i + r] = 0.0

        total += d2.sum()

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
