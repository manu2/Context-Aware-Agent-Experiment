import numpy as np

# Load array
X = np.load("vectors_secondary.npy")
N = X.shape[0]

# Convert to float64 for precision during dot product computation
X64 = X.astype(np.float64)
sq_norms = np.sum(X64**2, axis=1, keepdims=True)

total_dist = 0.0
batch_size = 1000

for i in range(0, N, batch_size):
    end = min(i + batch_size, N)
    # Compute squared Euclidean distances for the batch: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
    dot = np.dot(X64[i:end], X64.T)
    d2 = sq_norms[i:end] + sq_norms.T - 2.0 * dot
    np.maximum(d2, 0.0, out=d2)

    # Enforce exact zero on the diagonal
    for r in range(end - i):
        d2[r, i + r] = 0.0

    dists = np.sqrt(d2)
    total_dist += float(np.sum(dists))

print(f"TOTAL:{total_dist}")
