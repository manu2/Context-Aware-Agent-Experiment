import numpy as np

def main():
    # Load vectors, use float64 for accurate distance computation
    vecs = np.load("vectors.npy").astype(np.float64)
    n = vecs.shape[0]

    # squared norms of each row
    sq_norms = np.einsum('ij,ij->i', vecs, vecs)

    total = 0.0
    chunk_size = 500  # process rows in chunks to limit memory usage

    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        chunk = vecs[start:end]  # shape (c, d)

        # dot products between chunk and all vectors
        dots = chunk @ vecs.T  # shape (c, n)

        # squared distances: ||a||^2 + ||b||^2 - 2*a.b
        sq_dists = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * dots

        # numerical issues can cause tiny negative values; clip them
        np.maximum(sq_dists, 0.0, out=sq_dists)

        dists = np.sqrt(sq_dists)

        total += dists.sum()

    # Print with high precision decimal representation
    print(f"TOTAL:{total:.10f}")

if __name__ == "__main__":
    main()
