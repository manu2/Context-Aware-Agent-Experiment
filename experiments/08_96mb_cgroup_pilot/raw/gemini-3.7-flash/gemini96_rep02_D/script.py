import numpy as np


def main():
    # Load vector data (8000 x 1024, float32 -> ~32 MB)
    X = np.load("vectors.npy")
    n_vectors = X.shape[0]

    # Compute squared L2 norms per vector without extra large allocations: ||v_i||^2
    sq_norms = np.einsum("ij,ij->i", X, X)

    total_dist = 0.0
    batch_size = 500  # Process in blocks to strictly adhere to the 96 MB RAM limit

    for i in range(0, n_vectors, batch_size):
        # Compute G = X_batch @ X.T (batch_size x 8000 float32 -> ~16 MB)
        G = X[i : i + batch_size] @ X.T

        # Use ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v> in-place
        G *= -2.0
        G += sq_norms[i : i + batch_size, None]
        G += sq_norms[None, :]

        # Clamp small negative values resulting from numerical precision issues
        np.maximum(G, 0.0, out=G)
        np.sqrt(G, out=G)

        total_dist += float(np.sum(G))

    print(f"TOTAL_DIST:{total_dist}")


if __name__ == "__main__":
    main()