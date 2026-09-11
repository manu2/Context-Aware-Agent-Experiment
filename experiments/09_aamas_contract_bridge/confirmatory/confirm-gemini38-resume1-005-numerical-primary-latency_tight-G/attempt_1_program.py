import numpy as np


def main():
    # Load the vectors and convert to float64 for numerical precision
    vectors = np.load("vectors.npy").astype(np.float64)
    n, d = vectors.shape

    # Preallocate reusable buffers to avoid unnecessary allocations
    buf = np.empty((n - 1, d), dtype=np.float64)
    sq_buf = np.empty(n - 1, dtype=np.float64)

    total_upper = 0.0
    # Iterate over all pairs (i, j) with i < j
    for i in range(n - 1):
        rem = n - 1 - i

        # Compute differences: vectors[i + 1:] - vectors[i]
        diff = np.subtract(vectors[i + 1 :], vectors[i], out=buf[:rem])

        # In-place square and sum along dimension axis
        np.square(diff, out=diff)
        sq = np.sum(diff, axis=1, out=sq_buf[:rem])

        # In-place square root to get Euclidean distances
        np.sqrt(sq, out=sq)

        total_upper += np.sum(sq)

    # Sum over all ordered pairs:
    # d(i, j) = d(j, i) for i != j, and d(i, i) = 0 for the diagonal
    total = total_upper * 2.0

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
