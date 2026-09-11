import numpy as np


def main():
    X = np.load("vectors.npy")

    norms = np.sum(X * X, axis=1, keepdims=True)

    G = X @ X.T
    G *= -2.0
    G += norms
    G += norms.T

    np.maximum(G, 0.0, out=G)
    np.fill_diagonal(G, 0.0)
    np.sqrt(G, out=G)

    total = float(np.sum(G, dtype=np.float64))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
