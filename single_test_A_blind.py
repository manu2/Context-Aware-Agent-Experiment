import numpy as np
import os

def compute_total_pairwise_dot_product_sum(file_path='vectors.npy'):
    """
    Loads a matrix from a .npy file, computes the total sum of all pairwise
    row dot products, and prints the result.

    Args:
        file_path (str): The path to the .npy file containing the matrix.
    """

    # --- Create a dummy vectors.npy file if it doesn't exist ---
    # This makes the script self-contained and runnable without prior setup.
    expected_shape = (8000, 1024)
    expected_dtype = np.float32

    if not os.path.exists(file_path):
        print(f"'{file_path}' not found. Creating a dummy file for demonstration...")
        # Generate random data matching the specified dimensions and dtype
        dummy_matrix = np.random.rand(*expected_shape).astype(expected_dtype) * 10.0
        np.save(file_path, dummy_matrix)
        print(f"Dummy '{file_path}' created with shape {dummy_matrix.shape} and dtype {dummy_matrix.dtype}.")
    # -----------------------------------------------------------

    # Load the matrix from the .npy file
    try:
        vectors = np.load(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except Exception as e:
        print(f"Error loading '{file_path}': {e}")
        return

    # Optional: Verify the loaded matrix's shape and dtype
    if vectors.shape != expected_shape or vectors.dtype != expected_dtype:
        print(f"Warning: Loaded matrix has shape {vectors.shape} and dtype {vectors.dtype}.")
        print(f"         Expected shape {expected_shape} and dtype {expected_dtype}.")
        # The calculation will still proceed with the loaded data.

    # Step 1: Compute the sum of all rows.
    # np.sum(axis=0) sums elements along the columns, effectively producing
    # a single vector where each element is the sum of the corresponding column.
    sum_of_all_rows = np.sum(vectors, axis=0)

    # Step 2: Compute the dot product of this sum vector with itself.
    # This efficiently calculates sum_{i,j} (A[i] . A[j]).
    total_sum_of_pairwise_dot_products = np.dot(sum_of_all_rows, sum_of_all_rows)

    # Print the result in the specified format
    print(f"TOTAL_SUM:{total_sum_of_pairwise_dot_products}")

if __name__ == "__main__":
    compute_total_pairwise_dot_product_sum()