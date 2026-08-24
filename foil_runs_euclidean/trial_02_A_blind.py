import numpy as np

def calculate_pairwise_euclidean_sum(vectors_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix loaded from a .npy file.

    The matrix is expected to be 8000x1024 float32.
    The calculation uses a memory-efficient vectorized approach for the inner loop.

    Args:
        vectors_path (str): The path to the .npy file containing the matrix.
    """
    try:
        # Load the matrix from the .npy file
        V = np.load(vectors_path)
    except FileNotFoundError:
        print(f"Error: '{vectors_path}' not found. Please ensure the file exists in the same directory.")
        return
    except Exception as e:
        print(f"An error occurred while loading '{vectors_path}': {e}")
        return

    # Ensure the matrix is of type float32 as specified.
    # np.load typically preserves the original dtype, but this adds robustness.
    if V.dtype != np.float32:
        print(f"Warning: Input matrix dtype is {V.dtype}, converting to float32.")
        V = V.astype(np.float32)

    N, D = V.shape

    # Initialize total_distance_sum as a float64 to accumulate sums with high precision.
    total_distance_sum = 0.0

    # Iterate through each vector v_i in the matrix V
    for i in range(N):
        # Calculate the difference between the current vector v_i and all other vectors v_j.
        # V[i, :] is a (D,) vector. V is an (N, D) matrix.
        # NumPy's broadcasting rules handle this subtraction efficiently,
        # effectively expanding V[i, :] to (N, D) for the operation.
        # The result 'diffs' will have shape (N, D) and dtype float32.
        diffs = V[i, :] - V

        # Square each element of the differences.
        # 'sq_diffs' will also have shape (N, D) and dtype float32.
        sq_diffs = diffs * diffs

        # Sum the squared differences along the feature dimension (axis=1).
        # This computes ||v_i - v_j||^2 for all j, resulting in an (N,) array of float32.
        sum_sq_diffs = np.sum(sq_diffs, axis=1)

        # Take the square root to get the Euclidean distances.
        # np.maximum(sum_sq_diffs, 0.0) is used to prevent issues with sqrt of
        # very small negative numbers that can arise from floating-point inaccuracies
        # (e.g., when v_i == v_j, sum_sq_diffs should be 0 but might be -1e-10).
        # 'distances_from_vi' will be an (N,) array of float32.
        distances_from_vi = np.sqrt(np.maximum(sum_sq_diffs, 0.0))

        # Sum all distances from v_i to all v_j and add to the total.
        # np.sum on a float32 array returns a float32 sum. Adding this to the
        # float64 'total_distance_sum' promotes the sum to float64 before addition,
        # maintaining overall precision.
        total_distance_sum += np.sum(distances_from_vi)

    # Print the final result in the specified format.
    print(f"TOTAL_DIST:{total_distance_sum}")

if __name__ == "__main__":
    # This block ensures the function runs when the script is executed directly.
    # For testing purposes, you might want to create a dummy 'vectors.npy' file
    # if it doesn't exist. For the final solution, we assume it's present.
    
    # Example of creating a dummy file for local testing (uncomment to use):
    # if not np.os.path.exists('vectors.npy'):
    #     print("Creating a dummy 'vectors.npy' for demonstration...")
    #     dummy_N = 100 # Smaller N for quick testing
    #     dummy_D = 10  # Smaller D for quick testing
    #     dummy_vectors = np.random.rand(dummy_N, dummy_D).astype(np.float32)
    #     np.save('vectors.npy', dummy_vectors)
    #     print(f"Dummy file created with shape {dummy_vectors.shape}.")

    calculate_pairwise_euclidean_sum()