import numpy as np
import os

def compute_pairwise_dot_product_sum(file_path='vectors.npy'):
    """
    Loads a matrix from a .npy file, computes the total sum of all pairwise
    row dot products, and prints the result.

    Args:
        file_path (str): The path to the .npy file containing the matrix.
    """
    # --- Create a dummy file if 'vectors.npy' does not exist ---
    # This block makes the script self-contained and runnable without
    # requiring the user to manually create the file first.
    # In a production environment, you would typically expect the file to exist.
    if not os.path.exists(file_path):
        print(f"'{file_path}' not found. Creating a dummy file for demonstration.")
        N_rows = 8000
        D_cols = 1024
        # Using np.random.rand to generate values between 0.0 and 1.0
        # and casting to float32 as per problem description.
        dummy_vectors = np.random.rand(N_rows, D_cols).astype(np.float32)
        np.save(file_path, dummy_vectors)
        print(f"Dummy '{file_path}' ({N_rows}x{D_cols} float32) created.")
    # --- End of dummy file creation ---

    # Load the matrix from the .npy file
    try:
        vectors = np.load(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except Exception as e:
        print(f"Error loading '{file_path}': {e}")
        return

    # Validate the matrix shape and data type
    expected_shape = (8000, 1024)
    expected_dtype = np.float32
    if vectors.shape != expected_shape or vectors.dtype != expected_dtype:
        print(f"Warning: Expected matrix shape {expected_shape} and dtype {expected_dtype}, "
              f"but got {vectors.shape} and {vectors.dtype}.")
        print("Proceeding with computation, but results might differ if data is not as expected.")

    # Compute the matrix product V @ V.T
    # This results in an N x N matrix where M_ij = dot(row_i, row_j)
    pairwise_dot_products_matrix = vectors @ vectors.T

    # Sum all elements of the resulting matrix
    # It's good practice to sum in float64 to maintain precision,
    # especially when summing a large number of float32 values.
    total_sum = np.sum(pairwise_dot_products_matrix, dtype=np.float64)

    # Print the result in the specified format
    print(f"TOTAL_SUM:{total_sum}")

if __name__ == "__main__":
    compute_pairwise_dot_product_sum()