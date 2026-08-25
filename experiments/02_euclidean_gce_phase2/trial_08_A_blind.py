#!/usr/bin/env python3

import numpy as np
import os

def main():
    # Define the filename for the vector data
    filename = 'vectors.npy'

    # --- Create a dummy 'vectors.npy' file for testing if it doesn't exist ---
    # In a real scenario, this file would be provided.
    # This block ensures the script is runnable out-of-the-box for demonstration.
    if not os.path.exists(filename):
        print(f"'{filename}' not found. Creating a dummy file for demonstration purposes...")
        # Create an 8000 x 1024 matrix of random float32 values
        # Using a fixed seed for reproducibility of the dummy data
        np.random.seed(42) 
        dummy_vectors = np.random.rand(8000, 1024).astype(np.float32)
        np.save(filename, dummy_vectors)
        print(f"Dummy '{filename}' (8000x1024 float32) created.")
    # -------------------------------------------------------------------------

    # Load the vectors from the .npy file
    # Ensure the data is loaded as float32 as specified.
    # numpy.load typically preserves the original dtype.
    vectors = np.load(filename)

    # Verify the shape and dtype of the loaded data
    expected_shape = (8000, 1024)
    if vectors.shape != expected_shape:
        raise ValueError(f"Expected matrix shape {expected_shape}, but got {vectors.shape}")
    if vectors.dtype != np.float32:
        # Convert to float32 if it's not already, as per problem spec for input.
        # Note: Intermediate calculations (like dot product) might promote to float64
        # for better precision, which is generally desirable.
        print(f"Warning: Input data was not float32 ({vectors.dtype}), converting to np.float32.")
        vectors = vectors.astype(np.float32)

    N, D = vectors.shape

    # Calculate the squared L2 norms for each vector: ||v_i||^2
    # This is sum_k (v_i[k]^2)
    # The result will be a 1D array of shape (N,)
    sq_norms = np.sum(vectors**2, axis=1)

    # Calculate the dot product matrix V @ V.T
    # This matrix has elements M_ij = v_i . v_j
    # NumPy's np.dot (or @ operator) for float32 inputs will typically
    # promote the output to float64 for better precision. This is generally
    # desirable for numerical stability when summing many products.
    dot_product_matrix = np.dot(vectors, vectors.T)

    # Calculate the squared Euclidean distance matrix using the formula:
    # ||v_i - v_j||^2 = ||v_i||^2 - 2 * (v_i . v_j) + ||v_j||^2
    #
    # sq_norms[:, np.newaxis] reshapes (N,) to (N, 1)
    # sq_norms[np.newaxis, :] reshapes (N,) to (1, N)
    # These are broadcasted against the (N, N) dot_product_matrix.
    # The result will be an (N, N) matrix of squared distances.
    # The dtype will be float64 due to promotion from dot_product_matrix.
    squared_distances = sq_norms[:, np.newaxis] - 2 * dot_product_matrix + sq_norms[np.newaxis, :]

    # Due to potential floating point inaccuracies, some elements in
    # squared_distances might be very small negative numbers (e.g., -1e-9).
    # Since distance squared cannot be negative, clamp these to zero before
    # taking the square root.
    squared_distances[squared_distances < 0] = 0.0

    # Take the square root to get the actual Euclidean distances
    distances = np.sqrt(squared_distances)

    # Sum all pairwise distances
    # This sum includes distances from i to j and j to i, and 0 for i to i,
    # which matches the sum_{i,j} definition.
    total_distance = np.sum(distances)

    # Print the result in the specified format
    print(f"TOTAL_DIST:{total_distance}")

if __name__ == "__main__":
    main()