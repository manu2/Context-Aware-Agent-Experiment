import numpy as np

def main():
    V = np.load('vectors.npy', mmap_mode='r')
    n = V.shape[0]

    # Compute squared norms in float64 for accuracy
    norms = np.empty(n, dtype=np.float64)
    B = 500
    for i in range(0, n, B):
        block = V[i:i+B].astype(np.float64)
        norms[i:i+B] = np.sum(block * block, axis=1)

    total = 0.0
    for i in range(0, n, B):
        block_i = V[i:i+B].astype(np.float64)
        # process column blocks too, to limit memory
        row_sum = np.zeros(block_i.shape[0], dtype=np.float64)
        for j in range(0, n, B):
            block_j = V[j:j+B].astype(np.float64)
            dots = block_i @ block_j.T
            d2 = norms[i:i+B, None] + norms[None, j:j+B] - 2.0 * dots
            np.maximum(d2, 0.0, out=d2)
            np.sqrt(d2, out=d2)
            row_sum += d2.sum(axis=1)
        total += row_sum.sum()

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
