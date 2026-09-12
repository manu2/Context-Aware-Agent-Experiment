import numpy as np


def main():
    X = np.load("vectors.npy")
    N, D = X.shape

    # Precompute squared L2 norms for each row without allocating large temporaries
    sq_norms = np.einsum("ij,ij->i", X, X)

    # Process in chunks of rows to stay well under the 128 MiB peak memory limit
    chunk_size = 500
    G = np.empty((chunk_size, N), dtype=np.float32)

    total = 0.0
    zero_f32 = np.float32(0.0)
    neg_two = np.float32(-2.0)

    for i in range(0, N, chunk_size):
        chunk = X[i : i + chunk_size]
        B = len(chunk)

        # Compute dot products in-place: G = chunk @ X.T
        target_G = G[:B]
        np.matmul(chunk, X.T, out=target_G)

        # Compute squared Euclidean distance: ||x||^2 + ||y||^2 - 2*(x . y)
        target_G *= neg_two
        target_G += sq_norms[i : i + B, None]
        target_G += sq_norms[None, :]

        # Clamp negative values from rounding errors and take square root
        np.maximum(target_G, zero_f32, out=target_G)
        np.sqrt(target_G, out=target_G)

        # Strictly zero out self-distances on the diagonal
        for r in range(B):
            target_G[r, i + r] = 0.0

        total += float(target_G.sum(dtype=np.float64))

    print(f"TOTAL:{total}")


if __name__ == "__main__":
    main()
