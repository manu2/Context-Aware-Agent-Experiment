import numpy as np

# Load data
X = np.load('vectors_secondary.npy')  # shape (8000, 1024), float32
N = X.shape[0]

# Precompute squared norms in float64 for numerical stability
norms = np.einsum('ij,ij->i', X, X).astype(np.float64)

total = 0.0
block_size = 1000  # tune for memory/time balance

for start in range(0, N, block_size):
    end = min(start + block_size, N)
    Xi = X[start:end]                     # (b, 1024) float32
    dot = Xi @ X.T                         # (b, N) float32, BLAS matmul
    # squared distances in float64
    d2 = norms[start:end, None] + norms[None, :] - 2.0 * dot.astype(np.float64)
    np.maximum(d2, 0.0, out=d2)            # guard against tiny negative values
    dist = np.sqrt(d2)
    total += dist.sum(dtype=np.float64)

print(f"TOTAL:{total}")
