import numpy as np


def main():
    # Load the vectors
    vectors = np.load("vectors.npy")
    N, D = vectors.shape

    # Cast to float64 to ensure numerical precision and avoid cancellation issues
    vectors_64 = vectors.astype(np.float64)
    del vectors

    # Precompute squared L2 norms of each row
    sq_norms = np.sum(vectors_64**2, axis=1)

    total = 0.0
    batch_size = 1000

    # Process in row batches to strictly bound memory usage
    for start in range(0, N, batch_size):
        end = min(start + batch_size, N)
        v_batch = vectors_64[start:end]

        # ||u - v||^2 = ||u||^2 + ||v||^2 - 2 <u, v>
        dist_sq = (
            sq_norms[start:end, None]
            + sq_norms[None, :]
            - 2.0 * (v_batch @ vectors_64.T)
        )

        # Set diagonal entries (self-distances) strictly to 0.0
        diag_idx = np.arange(end - start)
        dist_sq[diag_idx, start + diag_idx] = 0.0

        # Guard against small negative values caused by floating-point imprecision
        np.maximum(dist_sq, 0.0, out=dist_sq)

        # Compute Euclidean distance in-place
        dists = np.sqrt(dist_sq, out=dist_sq)

        total += float(np.sum(dists))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
