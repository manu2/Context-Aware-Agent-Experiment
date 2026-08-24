import os
import sys
import numpy as np

def calculate_total_pairwise_euclidean_distance(file_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix stored in a .npy file.

    The calculation is sum_{i,j} ||v_i - v_j||_2, where v_i and v_j are rows
    of the matrix. This is equivalent to 2 * sum_{i<j} ||v_i - v_j||_2,
    as ||v_i - v_i||_2 = 0 and ||v_i - v_j||_2 = ||v_j - v_i||_2.

    Args:
        file_path (str): The path to the .npy file containing the matrix.

    Returns:
        float: The total sum of pairwise Euclidean distances.
    """
    try:
        # Load the matrix from the .npy file
        vectors = np.load(file_path)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found. Please ensure the file is in the same directory.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure the loaded data has the expected type (float32)
    # The problem states it's float32, but a conversion step adds robustness.
    if vectors.dtype != np.float32:
        print(f"Warning: Input matrix has dtype {vectors.dtype}, converting to float32.", file=sys.stderr)
        vectors = vectors.astype(np.float32)

    N, D = vectors.shape

    # Verify matrix dimensions if specific dimensions are expected (e.g., 8000x1024)
    # This check is optional but good for debugging if the input file is unexpected.
    if N != 8000 or D != 1024:
        print(f"Warning: Input matrix has shape {vectors.shape}, expected (8000, 1024). "
              "Proceeding with loaded shape.", file=sys.stderr)

    # Initialize the total distance accumulator
    total_distance = 0.0

    # Iterate through all unique pairs (i, j) where i < j
    # This approach is memory-efficient as it avoids creating a large
    # N x N distance matrix, which would exceed the 128 MB RAM limit.
    # The main matrix (8000x1024 float32) is ~31.25 MB.
    for i in range(N):
        # Get the i-th vector. This typically returns a view, not a copy.
        v_i = vectors[i, :]
        for j in range(i + 1, N):
            # Get the j-th vector.
            v_j = vectors[j, :]
            
            # Calculate the Euclidean distance between v_i and v_j.
            # ||v_i - v_j||_2 = np.linalg.norm(v_i - v_j)
            # np.linalg.norm is an optimized function for computing vector norms.
            distance = np.linalg.norm(v_i - v_j)
            total_distance += distance

    # The loop sums ||v_i - v_j||_2 only for i < j.
    # To get sum_{i,j} ||v_i - v_j||_2, we need to account for:
    # 1. Terms where i = j: ||v_i - v_i||_2 = 0. These don't contribute.
    # 2. Terms where j < i: ||v_j - v_i||_2. Since Euclidean distance is symmetric,
    #    ||v_j - v_i||_2 = ||v_i - v_j||_2.
    # Therefore, the total sum is 2 * (sum of distances for i < j).
    total_distance *= 2

    return total_distance

if __name__ == "__main__":
    # --- Self-contained script setup for execution ---
    # This block creates a dummy 'vectors.npy' if it doesn't exist.
    # This is for testing purposes, allowing the script to run out-of-the-box.
    # In a real execution environment where 'vectors.npy' is provided,
    # this block would typically be removed or commented out.
    if not os.path.exists('vectors.npy'):
        print("Creating dummy 'vectors.npy' (8000x1024 float32) for testing purposes...")
        # Use a fixed seed for reproducibility of dummy data
        np.random.seed(42)
        # Create a matrix of 8000 rows and 1024 columns, filled with random float32 values
        dummy_vectors = np.random.rand(8000, 1024).astype(np.float32)
        np.save('vectors.npy', dummy_vectors)
        print("Dummy 'vectors.npy' created.")
        print(f"Dummy file size: {os.path.getsize('vectors.npy') / (1024**2):.2f} MB")
    # --- End of script setup ---

    # The script expects 'vectors.npy' to be in the current directory.
    result = calculate_total_pairwise_euclidean_distance('vectors.npy')

    # Print the result in the specified format
    print(f"TOTAL_DIST:{result}")