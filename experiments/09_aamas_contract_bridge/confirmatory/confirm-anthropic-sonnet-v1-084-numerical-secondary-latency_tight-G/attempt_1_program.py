import numpy as np

def main():
    X = np.load('vectors_secondary.npy')
    X = X.astype(np.float64, copy=False)
    N = X.shape[0]

    norms = np.einsum('ij,ij->i', X, X)

    total = 0.0
    block = 400  # tune for memory/time balance

    for start in range(0, N, block):
        end = min(start + block, N)
        Xi = X[start:end]

        # dot products between block rows and all rows
        dot = Xi @ X.T  # shape (block, N)

        # squared distances
        sq = norms[start:end, None] + norms[None, :] - 2.0 * dot
        np.maximum(sq, 0.0, out=sq)  # guard against tiny negative values from floating point

        dists = np.sqrt(sq)

        # only take j > i (global indices) to avoid double counting
        rows_idx = np.arange(start, end)
        cols_idx = np.arange(N)
        mask = cols_idx[None, :] > rows_idx[:, None]

        total += dists[mask].sum()

    total_result = total * 2.0  # account for ordered pairs (i,j) and (j,i); diagonal is zero anyway

    print(f"TOTAL:{total_result}")

if __name__ == '__main__':
    main()
