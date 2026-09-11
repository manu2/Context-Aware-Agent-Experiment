import numpy as np


def main():
    vectors = np.load("vectors.npy")
    n = vectors.shape[0]
    step = 200

    total_dist = 0.0

    for i in range(0, n, step):
        x_i = vectors[i : i + step]

        # Diagonal block: all pairs within x_i
        diff_diag = x_i[:, None, :] - x_i[None, :, :]
        np.square(diff_diag, out=diff_diag)
        s_diag = np.sum(diff_diag, axis=-1)
        np.sqrt(s_diag, out=s_diag)
        total_dist += float(np.sum(s_diag, dtype=np.float64))

        # Off-diagonal blocks: pairs between x_i and x_j
        for j in range(i + step, n, step):
            x_j = vectors[j : j + step]
            diff = x_i[:, None, :] - x_j[None, :, :]
            np.square(diff, out=diff)
            s = np.sum(diff, axis=-1)
            np.sqrt(s, out=s)
            total_dist += 2.0 * float(np.sum(s, dtype=np.float64))

    print(f"TOTAL:{total_dist}")


if __name__ == "__main__":
    main()
