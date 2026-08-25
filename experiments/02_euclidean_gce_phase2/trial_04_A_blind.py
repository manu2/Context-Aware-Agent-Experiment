import numpy as np
import os

# --- Dummy file creation for demonstration and testing ---
# This block creates a 'vectors.npy' file if it doesn't exist.
# In a real-world scenario, 'vectors.npy' would be provided.
if not os.path.exists('vectors.npy'):
    print("Creating dummy 'vectors.npy' for demonstration purposes...")
    # Define dimensions as per problem statement
    N_rows = 8000
    D_cols = 1024
    # Generate random float32 data. Using a fixed seed for reproducibility.
    np.random.seed(42) 
    dummy_vectors = np.random.rand(N_rows, D_cols).astype(np.float32)
    np.save('vectors.npy', dummy_vectors)
    print(f"Dummy 'vectors.npy' created with shape {dummy_vectors.shape} and dtype {dummy_vectors.dtype}.")
# --- End of dummy file creation ---

def calculate_pairwise_euclidean_distances_sum(file_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix loaded from a .npy file.

    Args:
        file_path (str): The path to the .npy file containing the matrix.

    Returns:
        float: The total sum of all pairwise Euclidean distances, or None if an error occurs.
    """
    try:
        V = np.load(file_path)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found. Please ensure the file exists in the same directory.")
        return None
    except Exception as e:
        print(f"Error loading '{file_path}': {e}")
        return None

    # Validate matrix dimensions and data type as per problem statement
    expected_shape = (8000, 1024)
    expected_dtype = np.float32
    if V.shape != expected_shape or V.dtype != expected_dtype:
        print(f"Warning: '{file_path}' has unexpected shape {V.shape} or dtype {V.dtype}.")
        print(f"Expected shape: {expected_shape}, Expected dtype: {expected_dtype}.")
        # The calculation will proceed, but results might differ if data is not as specified.

    N, D = V.shape

    # Step 1: Compute squared L2 norms for each row vector.
    # ||v_i||_2^2 = sum(v_i_k^2)
    # This results in a 1D array of shape (N,).
    row_norms_sq = np.sum(V**2, axis=1)

    # Step 2: Compute all pairwise dot products between row vectors.
    # v_i . v_j = sum(v_i_k * v_j_k)
    # This is efficiently computed by matrix multiplication V @ V.T.
    # This results in an (N, N) matrix.
    dot_products = V @ V.T

    # Step 3: Compute squared Euclidean distances using the formula:
    # ||v_i - v_j||_2^2 = ||v_i||_2^2 + ||v_j||_2^2 - 2 * (v_i . v_j)
    # We use broadcasting for row_norms_sq:
    # row_norms_sq[:, np.newaxis] reshapes (N,) to (N, 1)
    # row_norms_sq[np.newaxis, :] reshapes (N,) to (1, N)
    # The sum/subtraction then broadcasts to an (N, N) matrix.
    dist_sq = row_norms_sq[:, np.newaxis] + row_norms_sq[np.newaxis, :] - 2 * dot_products

    # Step 4: Handle potential floating point inaccuracies.
    # Due to precision issues, dist_sq can sometimes be slightly negative (e.g., -1e-7)
    # for distances that should be exactly zero (like a vector to itself).
    # np.sqrt of a negative number would yield NaN. We clip to 0.
    dist_sq = np.maximum(dist_sq, 0)

    # Step 5: Take the square root to get Euclidean distances.
    # This results in an (N, N) matrix of distances.
    distances = np.sqrt(dist_sq)

    # Step 6: Sum all pairwise distances.
    total_distance = np.sum(distances)

    return total_distance

if __name__ == "__main__":
    total_dist_value = calculate_pairwise_euclidean_distances_sum('vectors.npy')
    if total_dist_value is not None:
        print(f"TOTAL_DIST:{total_dist_value}")