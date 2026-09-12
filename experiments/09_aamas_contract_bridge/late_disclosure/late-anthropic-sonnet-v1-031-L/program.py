import numpy as np

# Load the data. Using mmap avoids pulling the whole 32MB file into RAM
# unnecessarily during the initial read, but we then materialize a
# contiguous float32 copy (32MB) since that is small and needed for
# fast BLAS matrix multiplication.
X_mm = np.load('vectors_secondary.npy', mmap_mode='r')
N, D = X_mm.shape
X = np.ascontiguousarray(X_mm, dtype=np.float32)  # ~32MB, does not modify file

# Precompute squared norms in double precision for numerical stability.
norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)  # shape (N,), float64

total = 0.0
block = 250  # tuned to keep peak memory well under 128MiB

XT = X.T  # view, no extra memory

for start in range(0, N, block):
    end = min(start + block, N)
    A = X[start:end]  # (b, D) float32, view

    # Dot products between block rows and all rows (float32 matmul, fast BLAS)
    dot = A @ XT  # shape (b, N), float32

    # Promote to float64 for the distance formula to reduce cancellation error
    dot64 = dot.astype(np.float64)

    # squared distances: ||a||^2 + ||b||^2 - 2*a.b
    sq = norms[start:end, None] + norms[None, :] - 2.0 * dot64

    # Guard against tiny negative values due to floating point error
    np.maximum(sq, 0.0, out=sq)

    dist = np.sqrt(sq)

    total += float(dist.sum(dtype=np.float64))

    # free intermediate arrays explicitly
    del A, dot, dot64, sq, dist

print(f"TOTAL:{total}")
