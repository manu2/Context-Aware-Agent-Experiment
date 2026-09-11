import numpy as np


def main():
    vectors = np.load("vectors.npy")
    X = vectors.astype(np.float64)
    del vectors

    sq_norms = np.sum(X**2, axis=1)
    G = X @ X.T
    del X

    G *= -2.0
    G += sq_norms[:, None]
    G += sq_norms[None, :]
    np.maximum(G, 0.0, out=G)
    np.fill_diagonal(G, 0.0)
    np.sqrt(G, out=G)

    total = float(np.sum(G))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
