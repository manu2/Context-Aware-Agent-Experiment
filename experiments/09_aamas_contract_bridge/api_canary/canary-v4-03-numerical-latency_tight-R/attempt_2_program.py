import numpy as np


def main():
    X = np.load("vectors.npy").astype(np.float64)
    sq = np.sum(X**2, axis=1)

    # Compute pairwise squared Euclidean distances via Gram matrix
    D2 = np.dot(X, X.T)
    del X

    D2 *= -2.0
    D2 += sq[:, None]
    D2 += sq[None, :]
    np.fill_diagonal(D2, 0.0)
    np.maximum(D2, 0.0, out=D2)
    np.sqrt(D2, out=D2)

    total = float(np.sum(D2))
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
