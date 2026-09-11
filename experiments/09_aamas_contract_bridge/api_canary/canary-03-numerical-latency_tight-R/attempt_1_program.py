import numpy as np


def main():
    vectors = np.load("vectors.npy")
    X = vectors.astype(np.float64)

    sq_norms = np.sum(X**2, axis=1, keepdims=True)
    dist_sq = sq_norms + sq_norms.T - 2.0 * np.dot(X, X.T)
    np.maximum(dist_sq, 0.0, out=dist_sq)
    np.fill_diagonal(dist_sq, 0.0)

    dist = np.sqrt(dist_sq)
    total = np.sum(dist)

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
