import numpy as np
import os

# --- Start of dummy file creation for self-contained execution ---
# This block creates a 'vectors.npy' file if it doesn't exist.
# In a real-world scenario, you would typically provide this file.
dummy_filename = 'vectors.npy'
N_expected = 8000
D_expected = 1024

if not os.path.exists(dummy_filename):
    print(f"'{dummy_filename}' not found. Creating a dummy file with shape ({N_expected}, {D_expected}) and dtype float32...")
    # Use a fixed seed for reproducibility of dummy data
    np.random.seed(42)
    dummy_vectors = np.random.rand(N_expected, D_expected).astype(np.float32)
    np.save(dummy_filename, dummy_vectors)
    print("Dummy file created successfully.")
else:
    print(f"'{dummy_filename}' already exists. Using existing file.")
# --- End of dummy file creation ---

# 1. Load the matrix from 'vectors.npy'
try:
    V = np.load(dummy_filename)
except Exception as e:
    print(f"Error loading '{dummy_filename}': {e}")
    exit(1)

# Basic validation and type conversion
if V.shape != (N_expected, D_expected):
    print(f"Warning: Loaded matrix has shape {V.shape}, but expected ({N_expected}, {D_expected}). Proceeding anyway.")
if V.dtype != np.float32:
    print(f"Warning: Loaded matrix has dtype {V.dtype}, converting to float32.")
    V = V.astype(np.float32)

N, D = V.shape
print(f"Processing matrix with shape: {V.shape}, dtype: {V.dtype}")

# 2. Compute the squared L2 norms for each row vector.
# ||v_i||_2^2 = sum_k (v_ik^2)
# This results in a 1D array of shape (N,).
row_norms_sq = np.sum(V**2, axis=1)

# 3. Compute the matrix of all pairwise dot products.
# (V @ V.T)[i,j] = v_i . v_j
# This results in an N x N matrix.
dot_products = V @ V.T

# 4. Compute the squared Euclidean distances using the formula:
# ||v_i - v_j||_2^2 = ||v_i||_2^2 + ||v_j||_2^2 - 2 * (v_i . v_j)
# We use broadcasting to efficiently create the sum of squared norms matrix.
# row_norms_sq[:, np.newaxis] has shape (N, 1)
# row_norms_sq[np.newaxis, :] has shape (1, N)
# Their sum broadcasts to an (N, N) matrix where element (i,j) is ||v_i||_2^2 + ||v_j||_2^2.
sum_of_norms_sq = row_norms_sq[:, np.newaxis] + row_norms_sq[np.newaxis, :]
dist_sq = sum_of_norms_sq - 2 * dot_products

# Handle potential floating point inaccuracies: ensure non-negative values before taking the square root.
# This is important because `dist_sq[i,i]` should be 0, but might be a tiny negative number due to precision.
dist_sq = np.maximum(dist_sq, 0)

# 5. Compute the actual Euclidean distances by taking the square root.
dist = np.sqrt(dist_sq)

# 6. Sum all elements of the distance matrix to get the total pairwise distance.
# The sum includes dist[i,j] and dist[j,i] (which are equal) and dist[i,i] (which are 0).
total_distance = np.sum(dist)

# 7. Print the result in the specified format.
print(f"TOTAL_DIST:{total_distance}")

# Optional: Uncomment the following lines to remove the dummy file after execution.
# if 'dummy_vectors' in locals(): # Check if dummy_vectors was created by this script
#     os.remove(dummy_filename)
#     print(f"Cleaned up dummy file '{dummy_filename}'.")