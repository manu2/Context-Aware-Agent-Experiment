import numpy as np


def main():
    # Load vectors (8000 x 1024) and convert to float64 for precision
    vectors = np.load("vectors.npy").astype(np.float64)

    # Compute squared norms of each vector: shape (8000,)
    sq_norms = np.sum(vectors**2, axis=1)

    # Compute Gram matrix (pairwise dot products): shape (8000, 8000)
    gram = np.dot(vectors, vectors.T)

    # Compute squared Euclidean distances in-place: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
    gram *= -2.0
    gram += sq_norms[:, np.newaxis]
    gram += sq_norms[np.newaxis, :]

    # Clamp numerical underflows below 0 to 0.0
    np.maximum(gram, 0.0, out=gram)

    # Compute Euclidean distances
    np.sqrt(gram, out=gram)

    # Total sum of all pairwise distances
    total_dist = np.sum(gram)

    print(f"TOTAL_DIST:{total_dist}")


if __name__ == "__main__":
    main()