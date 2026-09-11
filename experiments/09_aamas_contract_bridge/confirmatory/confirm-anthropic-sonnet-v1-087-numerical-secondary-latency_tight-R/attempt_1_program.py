import numpy as np

# Load data (do not modify the original file)
X = np.load('vectors_secondary.npy').astype(np.float64)

# Compute squared norms of each row
sq = np.einsum('ij,ij->i', X, X)

# Compute Gram matrix (X @ X.T) using BLAS for speed
G = X @ X.T

# Compute squared distances: ||xi||^2 + ||xj||^2 - 2*xi.xj
D2 = sq[:, None] + sq[None, :] - 2.0 * G

# Numerical noise can make tiny negative values on the diagonal or elsewhere; clip them
np.maximum(D2, 0.0, out=D2)

# Euclidean distances
D = np.sqrt(D2)

# Sum over all ordered pairs (including zero diagonal)
total = np.sum(D)

print(f"TOTAL:{total!r}")
