#!/usr/bin/env python3

import numpy as np
import os
import sys

def calculate_pairwise_euclidean_distances_sum(vectors_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix stored in a .npy file.

    Args:
        vectors_path (str): Path to the .npy file containing the matrix.
                            Expected to be an 8000 x 1024 float32 matrix.

    Returns:
        float: The total sum of all pairwise Euclidean distances.
    """
    # --- Self-contained dummy data generation for demonstration ---
    if not os.path.exists(vectors_path):
        print(f"'{vectors_path}' not found. Creating a dummy file with specified dimensions (8000x1024 float32) for demonstration.", file=sys.stderr)
        N_dummy, D_dummy = 8000, 1024
        # Generate random float32 data
        dummy_vectors = np.random.rand(N_dummy, D_dummy).astype(np.float32)
        np.save(vectors_path, dummy_vectors)
        print(f"Dummy '{vectors_path}' created. This file will be used for calculation.", file=sys.stderr)
    # --- End of dummy data generation ---

    # Load the matrix from the .npy file
    V = np.load(vectors_path)

    # Ensure the data type is float32 as specified.
    # np.load usually preserves the original dtype, but this is a safeguard.
    if V.dtype != np.float32:
        print(f"Warning: Input matrix dtype is {V.dtype}, converting to float32.", file=sys.stderr)
        V = V.astype(np.float32)

    # N is the number of vectors (rows), D is the dimensionality
    N, D = V.shape
    print(f"Processing matrix of shape {N}x{D} with dtype {V.dtype}", file=sys.stderr)

    # Step 1: Calculate squared L2 norms for each vector: ||v_i||^2
    # This is sum_k (v_ik)^2 for each row v_i.
    # Resulting shape: (N,)
    sq_norms = np.sum(V**2, axis=1)

    # Step 2: Calculate the dot product matrix: V @ V.T
    # This gives v_i . v_j for all pairs (i, j).
    # Resulting shape: (N, N)
    # For float32 inputs, numpy's matmul (@) typically produces float32 output.
    dot_products = V @ V.T

    # Step 3: Calculate the squared Euclidean distance matrix using the formula:
    # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * (v_i . v_j)
    # sq_norms[:, np.newaxis] broadcasts (N,1) with sq_norms[np.newaxis,:] (1,N)
    # to produce an (N,N) matrix where element (i,j) is ||v_i||^2 + ||v_j||^2.
    # Resulting shape: (N, N)
    dist_sq_matrix = sq_norms[:, np.newaxis] + sq_norms[np.newaxis, :] - 2 * dot_products

    # Step 4: Handle potential floating point inaccuracies.
    # Due to floating point arithmetic, dist_sq_matrix can have very small negative values
    # (e.g., -1e-9) when two vectors are identical or very close.
    # Clipping these to 0 prevents np.sqrt from producing NaNs.
    dist_sq_matrix = np.maximum(dist_sq_matrix, 0)

    # Step 5: Take the square root to get the actual Euclidean distances.
    # Resulting shape: (N, N)
    dist_matrix = np.sqrt(dist_sq_matrix)

    # Step 6: Sum all elements in the distance matrix.
    # This includes distances from a vector to itself (which are 0)
    # and counts ||v_i - v_j|| and ||v_j - v_i|| separately (which are equal).
    total_dist = np.sum(dist_matrix)

    return total_dist

if __name__ == "__main__":
    # The script expects 'vectors.npy' in the same directory.
    # If it's not found, a dummy file will be created as specified (8000x1024 float32).
    
    print("Starting calculation...", file=sys.stderr)
    total_distance_sum = calculate_pairwise_euclidean_distances_sum()
    
    # Print the result in the specified format
    print(f"TOTAL_DIST:{total_distance_sum}")
    print("Calculation finished.", file=sys.stderr)