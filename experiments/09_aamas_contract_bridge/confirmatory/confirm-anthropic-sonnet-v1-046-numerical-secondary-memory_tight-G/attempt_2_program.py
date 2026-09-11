import numpy as np

# Load the input array (float32, 8000 x 1024)
X = np.load('vectors_secondary.npy')

n = X.shape[0]

# Use double precision for accurate distance computation
X64 = X.astype(np.float64)

# Precompute squared norms of each row
norms = np.einsum('ij,ij->i', X64, X64)

total = 0.0
B = 250  # block size to limit memory usage

for start in range(0, n, B):
    end = min(start + B, n)
    block = X64[start:end]           # (b, 1024)
    dots = block @ X64.T             # (b, n)
    d2 = norms[start:end][:, None] + norms[None, :] - 2.0 * dots
    np.maximum(d2, 0.0, out=d2)      # guard against tiny negative values from floating point error
    np.sqrt(d2, out=d2)
    total += d2.sum()
    del dots, d2

print(f"TOTAL:{total:.10f}")
