import numpy as np


def main():
    vectors = np.load("vectors.npy")
    X = vectors.astype(np.float64)
    del vectors

    sq = np.sum(X**2, axis=1)
    G = X @ X.T
    del X

    G *= -2.0
    G += sq[:, None]
    G += sq[None, :]

    np.maximum(G, 0.0, out=G)
    np.fill_diagonal(G, 0.0)
    np.sqrt(G, out=G)

    total = np.sum(G)
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
