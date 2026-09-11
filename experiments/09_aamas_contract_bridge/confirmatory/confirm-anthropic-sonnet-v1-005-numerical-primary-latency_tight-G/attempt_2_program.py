import numpy as np

def main():
    vecs = np.load("vectors.npy", mmap_mode="r")  # (8000, 1024) float32
    n = vecs.shape[0]

    # Work in float64 for accuracy, but keep memory bounded.
    # Load full array into memory as float64 once (8000*1024*8 bytes ~ 64MB)
    X = np.asarray(vecs, dtype=np.float64)

    # squared norms of each row
    sq_norms = np.einsum('ij,ij->i', X, X)

    block_size = 400  # tune for memory/time balance
    total = 0.0

    for start in range(0, n, block_size):
        end = min(start + block_size, n)
        block = X[start:end]  # (b, 1024)

        # dot products between block and all rows: (b, n)
        dots = block @ X.T

        # squared distances: ||a||^2 + ||b||^2 - 2*a.b
        sq_dist = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots

        # numerical noise can make tiny negatives; clip
        np.maximum(sq_dist, 0.0, out=sq_dist)

        dist = np.sqrt(sq_dist)

        total += dist.sum(dtype=np.float64)

    # Print total as decimal
    print(f"TOTAL:{total:.6f}")

if __name__ == "__main__":
    main()
