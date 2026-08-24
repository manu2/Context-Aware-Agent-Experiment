import numpy as np
import sys
import os

def calculate_total_pairwise_euclidean_distance(vectors_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix loaded from a .npy file.

    Args:
        vectors_path (str): The path to the .npy file containing the matrix.

    Prints:
        The total sum in the format 'TOTAL_DIST:<value>'.
    """
    try:
        V = np.load(vectors_path)
    except FileNotFoundError:
        print(f"Error: '{vectors_path}' not found. Please ensure the file exists.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading '{vectors_path}': {e}")
        sys.exit(1)

    # Ensure the matrix is float32 as specified.
    # numpy.load usually preserves dtype, but explicit conversion ensures compliance.
    if V.dtype != np.float32:
        V = V.astype(np.float32)

    N, D = V.shape

    # Initialize total_dist_half as a float64 to maintain precision for the sum.
    # Python's default float is float64, which is suitable for large sums.
    total_dist_half = 0.0 

    # Precompute squared norms for each vector (row)
    # sq_norms[k] = ||V[k,:]||^2
    # This results in an (N,) array of float32 values.
    sq_norms = np.sum(V**2, axis=1)

    # Iterate through each vector v_i
    # We calculate distances for pairs (v_i, v_j) where j > i to avoid
    # redundant calculations (||v_i - v_j|| = ||v_j - v_i||) and self-distances (||v_i - v_i|| = 0).
    # The final total sum will be 2 * total_dist_half.
    for i in range(N):
        v_i = V[i, :] # Current vector (D,)

        # Calculate dot products of v_i with all subsequent vectors V[j,:] where j > i.
        # V[i+1:, :] is a view of the matrix containing rows from i+1 to N-1.
        # The result is an (N-i-1,) array.
        dot_products_with_vi_slice = V[i+1:, :] @ v_i

        # Calculate squared Euclidean distances using the formula:
        # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * (v_i . v_j)
        # sq_norms[i] is ||v_i||^2 (scalar)
        # sq_norms[i+1:] is an array of ||v_j||^2 for j > i (N-i-1,)
        # dot_products_with_vi_slice is an array of v_j . v_i for j > i (N-i-1,)
        sq_dists_slice = sq_norms[i] + sq_norms[i+1:] - 2 * dot_products_with_vi_slice
        
        # Due to floating point inaccuracies, sq_dists_slice can sometimes be
        # slightly negative (e.g., -1e-7). Clip to 0 to avoid sqrt of negative numbers.
        sq_dists_slice = np.maximum(sq_dists_slice, 0.0)

        # Take the square root to get Euclidean distances
        dists_slice = np.sqrt(sq_dists_slice)
        
        # Sum these distances and add to the running total.
        # np.sum(dists_slice) will be float32, but adding to total_dist_half (float64)
        # promotes it to float64, preserving precision.
        total_dist_half += np.sum(dists_slice)

    # The total sum of all pairwise distances (sum_{i,j} ||v_i - v_j||_2)
    # is 2 * sum_{i<j} ||v_i - v_j||_2, because ||v_i - v_j|| = ||v_j - v_i||
    # and ||v_i - v_i|| = 0.
    total_dist = 2 * total_dist_half

    print(f"TOTAL_DIST:{total_dist}")

if __name__ == "__main__":
    # To run this script, ensure 'vectors.npy' exists in the same directory
    # or provide its full path.
    # For testing purposes, you can uncomment the following block to create
    # a dummy 'vectors.npy' file of the specified size.
    # This dummy file creation will take some time and disk space.
    #
    # if not os.path.exists('vectors.npy'):
    #     print("Creating a dummy 'vectors.npy' for testing. This will take a moment...")
    #     N_dummy = 8000
    #     D_dummy = 1024
    #     np.random.seed(42) # For reproducibility
    #     V_dummy = np.random.rand(N_dummy, D_dummy).astype(np.float32)
    #     np.save('vectors.npy', V_dummy)
    #     print(f"Dummy 'vectors.npy' created with shape {V_dummy.shape}.")
    #     print("Please note: The calculation for 8000x1024 matrix can take several minutes.")
    
    calculate_total_pairwise_euclidean_distance()