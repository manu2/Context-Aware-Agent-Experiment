import numpy as np


def main():
    # Load the vectors
    vectors = np.load("vectors.npy")

    # Cast to float64 to ensure high numerical precision and prevent overflow/cancellation
    X = vectors.astype(np.float64)
    del vectors

    # Compute squared norms: ||x_i||^2
    sq_norms = np.sum(X**2, axis=1)

    # Compute Gram matrix: X @ X.T
    gram = np.dot(X, X.T)
    del X

    # Compute pairwise squared Euclidean distances in-place:
    # ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * (x_i . x_j)
    gram *= -2.0
    gram += sq_norms[:, None]
    gram += sq_norms[None, :]

    # Clamp small negative values caused by floating-point inaccuracy to zero
    np.maximum(gram, 0.0, out=gram)
    np.sqrt(gram, out=gram)

    # Diagonal distances are zero
    np.fill_diagonal(gram, 0.0)

    total = float(np.sum(gram))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
