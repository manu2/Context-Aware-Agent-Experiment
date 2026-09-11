import numpy as np

# Load the vectors (do not modify the original file)
vectors = np.load('vectors.npy')

# Use float64 for higher precision in distance computations
v = vectors.astype(np.float64)

n = v.shape[0]

# Compute squared norms of each row
sq_norms = np.einsum('ij,ij->i', v, v)

# Compute Gram matrix (dot products between all pairs of rows)
gram = v @ v.T

# Compute squared distances using ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a.b
dist_sq = sq_norms[:, None] + sq_norms[None, :] - 2.0 * gram

# Numerical issues might make some values slightly negative; clip them
np.maximum(dist_sq, 0.0, out=dist_sq)

# Compute Euclidean distances
dist = np.sqrt(dist_sq)

# Sum all pairwise distances (including zero diagonal)
total = np.sum(dist, dtype=np.float64)

print(f"TOTAL:{total:.10f}")
