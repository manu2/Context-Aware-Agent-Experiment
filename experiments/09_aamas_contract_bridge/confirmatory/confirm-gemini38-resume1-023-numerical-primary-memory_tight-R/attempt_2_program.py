import numpy as np


def main():
    vectors = np.load("vectors.npy")
    n = len(vectors)
    total = 0.0

    for i in range(n - 1):
        diff = vectors[i + 1 :] - vectors[i]
        diff *= diff
        sq = np.sum(diff, axis=1, dtype=np.float64)
        total += np.sum(np.sqrt(sq))

    total *= 2.0
    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
