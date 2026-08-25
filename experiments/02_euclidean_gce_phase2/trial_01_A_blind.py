import numpy as np
import os
import sys

def calculate_pairwise_euclidean_sum(filename='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix loaded from a .npy file.

    Args:
        filename (str): The path to the .npy file containing the matrix.

    Returns:
        float: The total sum of pairwise Euclidean distances.
    """
    try:
        V = np.load(filename)
    except FileNotFoundError:
        print(f"Error: '{filename}' not found. Please ensure the file is in the same directory.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

    # The problem states the matrix contains float32.
    # If the loaded matrix has a different dtype, convert it to float32
    # to ensure consistency and correct memory/performance characteristics.
    if V.dtype != np.float32:
        print(f"Warning: Input matrix has dtype {V.dtype}, converting to float32 as specified.", file=sys.stderr)
        V = V.astype(np.float32)

    N, D = V.shape
    print(f"Processing matrix with shape: {V.shape} and dtype: {V.dtype}", file=sys.stderr)

    # Calculate squared Euclidean distances using the formula:
    # ||a - b||^2 = ||a||^2 + ||b||^2 - 2 * a.T * b

    # 1. Calculate the squared L2 norm for each row vector.
    # This results in an array of shape (N,).
    # row_norms_sq[i] = sum_k (V[i,k]^2)
    row_norms_sq = np.sum(V**2, axis=1)

    # 2. Calculate the dot product matrix V @ V.T.
    # This results in an (N, N) matrix where element [i,j] is V[i] . V[j].
    # This is the most computationally intensive step: O(N^2 * D) operations.
    dot_products = V @ V.T

    # 3. Combine the above to form the squared Euclidean distance matrix.
    # Using broadcasting:
    # row_norms_sq[:, np.newaxis] creates an (N, 1) array.
    # row_norms_sq[np.newaxis, :] creates a (1, N) array.
    # The sum `row_norms_sq[:, np.newaxis] + row_norms_sq[np.newaxis, :]` broadcasts
    # to an (N, N) matrix where element [i,j] is ||V[i]||^2 + ||V[j]||^2.
    # Then subtract 2 * dot_products[i,j].
    dist_sq_matrix = row_norms_sq[:, np.newaxis] + row_norms_sq[np.newaxis, :] - 2 * dot_products

    # Due to floating point inaccuracies, some values in dist_sq_matrix might be
    # slightly negative (e.g., -1e-7). Euclidean distance squared cannot be negative,
    # so clip any negative values to 0 before taking the square root.
    dist_sq_matrix = np.maximum(dist_sq_matrix, 0)

    # 4. Take the square root of each element to get the Euclidean distance matrix.
    dist_matrix = np.sqrt(dist_sq_matrix)

    # 5. Sum all pairwise distances.
    # Using dtype=np.float64 for the sum ensures higher precision for the final
    # large sum, preventing potential overflow or loss of precision if the sum
    # were to exceed float32's capacity or precision limits.
    total_dist = np.sum(dist_matrix, dtype=np.float64)

    return total_dist

if __name__ == "__main__":
    # Flag to track if a dummy file was created by this script
    dummy_file_created = False
    filename = 'vectors.npy'

    # --- Dummy file creation (for testing purposes only) ---
    # This block allows the script to be run directly for testing without
    # needing a pre-existing 'vectors.npy'. For the actual problem,
    # 'vectors.npy' is expected to be provided.
    if not os.path.exists(filename):
        print(f"Warning: '{filename}' not found. Creating a dummy file for demonstration.", file=sys.stderr)
        print("For the full problem, ensure 'vectors.npy' (8000x1024 float32) is in the same directory.", file=sys.stderr)
        N_dummy = 1000 # Smaller N for faster dummy generation
        D_dummy = 100  # Smaller D for faster dummy generation
        dummy_data = np.random.rand(N_dummy, D_dummy).astype(np.float32)
        np.save(filename, dummy_data)
        print(f"Dummy '{filename}' created with shape {dummy_data.shape}.", file=sys.stderr)
        dummy_file_created = True
    # -------------------------------------------------------

    total_distance_sum = calculate_pairwise_euclidean_sum(filename)
    
    # Print the final result to standard output as required
    print(f"TOTAL_DIST:{total_distance_sum}")

    # Optional: Clean up dummy file if it was created by this script
    if dummy_file_created:
        print(f"Removing dummy '{filename}'...", file=sys.stderr)
        os.remove(filename)