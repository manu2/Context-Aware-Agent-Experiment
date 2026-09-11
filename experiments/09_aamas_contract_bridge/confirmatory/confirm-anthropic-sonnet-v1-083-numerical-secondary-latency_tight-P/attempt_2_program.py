import numpy as np

def main():
    data = np.load('vectors_secondary.npy')
    n, d = data.shape
    data = np.ascontiguousarray(data, dtype=np.float32)

    norms = np.einsum('ij,ij->i', data, data, dtype=np.float64).astype(np.float32)

    total_half = 0.0  # accumulate in float64 for precision

    block = 1000
    for i in range(0, n, block):
        bs = min(block, n - i)
        A = data[i:i + bs]          # (bs, d)
        B = data[i:]                 # (n-i, d)
        dot = A @ B.T                # (bs, n-i)

        nA = norms[i:i + bs].reshape(-1, 1)
        nB = norms[i:].reshape(1, -1)

        d2 = nA + nB - 2.0 * dot
        np.maximum(d2, 0.0, out=d2)
        dist = np.sqrt(d2, out=d2)   # (bs, n-i), float32

        # front part corresponds to the square block (bs x bs) - keep only strictly upper triangle
        front = dist[:, :bs]
        mask = np.triu(np.ones((bs, bs), dtype=bool), k=1)
        total_half += float(np.sum(front[mask], dtype=np.float64))

        # back part: columns from bs..(n-i-1) correspond to indices strictly greater than any row in this block
        if dist.shape[1] > bs:
            back = dist[:, bs:]
            total_half += float(np.sum(back, dtype=np.float64))

        del A, B, dot, d2, dist

    total = 2.0 * total_half
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
