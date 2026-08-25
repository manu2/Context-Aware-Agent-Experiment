import numpy as np
import os

def calculate_total_pairwise_euclidean_distance(file_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix stored in a .npy file.

    Args:
        file_path (str): The path to the .npy file containing the matrix.

    Returns:
        float: The total sum of all pairwise Euclidean distances.
    """
    # Ensure the input file exists
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' not found. Please ensure the file is in the same directory as the script.")
        exit(1)

    # Load the matrix. The problem states it's an 8,000 x 1,024 float32 matrix.
    vectors = np.load(file_path)

    # Sanity check for dimensions and dtype
    expected_shape = (8000, 1024)
    expected_dtype = np.float32
    if vectors.shape != expected_shape or vectors.dtype != expected_dtype:
        print(f"Warning: '{file_path}' has unexpected shape {vectors.shape} or dtype {vectors.dtype}.")
        print(f"Expected shape {expected_shape} and dtype {expected_dtype}. Proceeding anyway.")

    N, D = vectors.shape

    # Step 1: Calculate squared L2 norms for each row (||v_i||^2)
    # This results in an (N,) array of float32
    row_sq_norms = np.sum(vectors**2, axis=1)

    # Step 2: Calculate dot products between all pairs of rows (v_i . v_j)
    # This results in an (N, N) matrix of float32.
    # This is the most computationally intensive step: O(N^2 * D)
    dot_products = vectors @ vectors.T

    # Step 3: Expand row_sq_norms for broadcasting
    # sq_norms_i will be (N, 1)
    sq_norms_i = row_sq_norms[:, np.newaxis]
    # sq_norms_j will be (1, N)
    sq_norms_j = row_sq_norms[np.newaxis, :]

    # Step 4: Calculate squared Euclidean distances (||v_i - v_j||^2)
    # Formula: ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * (v_i . v_j)
    # np.maximum(..., 0) handles potential small negative values due to floating point inaccuracies
    # before taking the square root, preventing NaN results.
    squared_distances = np.maximum(sq_norms_i + sq_norms_j - 2 * dot_products, 0)

    # Step 5: Calculate Euclidean distances (||v_i - v_j||_2)
    # This results in an (N, N) matrix of float32
    distances = np.sqrt(squared_distances)

    # Step 6: Sum all pairwise distances.
    # Using dtype=np.float64 for the sum to maintain higher precision,
    # as summing many float32 values can lead to significant precision loss.
    total_distance = np.sum(distances, dtype=np.float64)

    return total_distance

if __name__ == "__main__":
    # Example: Create a dummy vectors.npy for testing if it doesn't exist.
    # This block can be removed if you are sure 'vectors.npy' will always be present.
    if not os.path.exists('vectors.npy'):
        print("Creating dummy 'vectors.npy' for testing purposes...")
        # Use smaller dimensions for quick testing
        N_dummy = 100
        D_dummy = 10
        dummy_vectors = np.random.rand(N_dummy, D_dummy).astype(np.float32)
        np.save('vectors.npy', dummy_vectors)
        print(f"Dummy 'vectors.npy' created with shape {dummy_vectors.shape} and dtype {dummy_vectors.dtype}")
        print("Please replace 'vectors.npy' with the actual file for the intended calculation.")
        # For the actual problem, the file is 8000x1024 float32.
        # If you want to test with the full size, uncomment the following lines
        # N_full = 8000
        # D_full = 1024
        # dummy_vectors_full = np.random.rand(N_full, D_full).astype(np.float32)
        # np.save('vectors.npy', dummy_vectors_full)
        # print(f"Dummy 'vectors.npy' created with shape {dummy_vectors_full.shape} and dtype {dummy_vectors_full.dtype}")


    # Perform the calculation
    result = calculate_total_pairwise_euclidean_distance('vectors.npy')

    # Print the result in the specified format
    print(f"TOTAL_DIST:{result}")