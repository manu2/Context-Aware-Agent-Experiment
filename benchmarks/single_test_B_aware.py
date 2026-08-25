import numpy as np
import os

def main():
    """
    Computes the total sum of all pairwise row dot products from 'vectors.npy'.
    The matrix is expected to be 8000x1024 float32.
    The computation is optimized for memory efficiency to stay within 128 MB RAM.
    """
    file_path = 'vectors.npy'

    # --- Dummy file creation for testing (remove or comment out for production if file is guaranteed) ---
    # This block creates a dummy 'vectors.npy' if it doesn't exist,
    # allowing the script to be run directly for testing purposes.
    if not os.path.exists(file_path):
        print(f"'{file_path}' not found. Creating a dummy file for demonstration.")
        dummy_N = 8000
        dummy_D = 1024
        # Using np.random.rand for float values, scaled to avoid very small numbers
        # and ensure a reasonable sum.
        dummy_matrix = np.random.rand(dummy_N, dummy_D).astype(np.float32) * 10.0
        np.save(file_path, dummy_matrix)
        print(f"Dummy '{file_path}' created with shape {dummy_matrix.shape} and dtype {dummy_matrix.dtype}.")
    # --------------------------------------------------------------------------------------------------

    try:
        # Load the matrix from the .npy file
        # Memory usage: 8000 * 1024 * 4 bytes = ~31.25 MB
        vectors = np.load(file_path)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found. Please ensure the file exists in the same directory.")
        return
    except Exception as e:
        print(f"An error occurred while loading '{file_path}': {e}")
        return

    # Optional: Verify the loaded matrix properties
    expected_shape = (8000, 1024)
    expected_dtype = np.float32
    if vectors.shape != expected_shape or vectors.dtype != expected_dtype:
        print(f"Warning: Expected matrix shape {expected_shape} and dtype {expected_dtype}, "
              f"but got {vectors.shape} and {vectors.dtype}. Proceeding anyway.")

    # Step 1: Calculate the sum of each column.
    # This results in a 1D array of shape (1024,)
    # Memory usage: 1024 * 4 bytes = 4 KB (negligible)
    column_sums = vectors.sum(axis=0)

    # Step 2: Square each element of the column sums.
    # Memory usage: 1024 * 4 bytes = 4 KB (negligible)
    squared_column_sums = column_sums**2

    # Step 3: Sum all the squared column sums to get the final total.
    # The result is a single float32 value.
    total_sum = squared_column_sums.sum()

    # Print the result in the specified format
    print(f"TOTAL_SUM:{total_sum}")

if __name__ == "__main__":
    main()