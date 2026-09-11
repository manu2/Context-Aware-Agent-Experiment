import numpy as np

# Load vectors and cast to float64 to ensure numerical precision
vectors = np.load("vectors.npy").astype(np.float64)

# Squared L2 norms of each vector: shape (8000,)
sq_norms = np.sum(vectors**2, axis=1)

# Gram matrix of dot products: shape (8000, 8000)
dist_sq = vectors @ vectors.T

# Compute squared Euclidean distances in-place to minimize memory usage:
# ||x_i - x_j||^2 = ||x_i||^2 + ||x_j||^2 - 2 * <x_i, x_j>
dist_sq *= -2.0
dist_sq += sq_norms[:, None]
dist_sq += sq_norms[None, :]

# Numerical safeguards: clamp negative values to 0 and ensure exact zero diagonal
np.maximum(dist_sq, 0.0, out=dist_sq)
np.fill_diagonal(dist_sq, 0.0)

# Compute Euclidean distances
np.sqrt(dist_sq, out=dist_sq)

# Sum across all ordered pairs
total = float(np.sum(dist_sq))

print(f"TOTAL:{total}")
