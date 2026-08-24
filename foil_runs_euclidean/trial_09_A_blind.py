import numpy as np
import sys
import os

def main():
    """
    Loads 'vectors.npy', computes the total sum of all pairwise Euclidean
    distances between its rows, and prints the result.
    """
    file_path = 'vectors.npy'

    # --- 1. Check for file existence ---
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' not found. Please ensure the file is in the same directory as the script.", file=sys.stderr)
        sys.exit(1)

    # --- 2. Load the matrix ---
    try:
        V = np.load(file_path)
    except Exception as e:
        print(f"Error loading '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- 3. Validate matrix dimensions and data type ---
    expected_shape = (8000, 1024)
    expected_dtype = np.float32

    if V.ndim != 2 or V.shape != expected_shape or V.dtype != expected_dtype:
        print(f"Error: Expected matrix of shape {expected_shape} and dtype {expected_dtype}, "
              f"but got {V.shape} and {V.dtype}.", file=sys.stderr)
        sys.exit(1)

    # --- 4. Compute squared Euclidean norms for each vector ---
    # ||v_i||^2 for each row v_i
    # Resulting shape: (N,)
    sq_norms = np.sum(V**2, axis=1)

    # --- 5. Compute the dot product matrix V @ V.T ---
    # This matrix contains (v_i . v_j) at position (i, j)
    # Resulting shape: (N, N)
    # This is the most computationally intensive step, but highly optimized by numpy's BLAS backend.
    dot_products = V @ V.T

    # --- 6. Compute the squared Euclidean distance matrix ---
    # D_ij^2 = ||v_i||^2 - 2 * (v_i . v_j) + ||v_j||^2
    # np.add.outer(sq_norms, sq_norms) efficiently computes sq_norms[i] + sq_norms[j] for all i, j
    # Resulting shape: (N, N)
    dist_sq_matrix = np.add.outer(sq_norms, sq_norms) - 2 * dot_products

    # --- 7. Handle potential floating point inaccuracies ---
    # Due to floating point arithmetic, very small negative values might appear
    # where the true distance is zero (e.g., for D_ii). np.sqrt on negative numbers
    # would result in NaN. We clip these to 0.
    dist_sq_matrix = np.maximum(dist_sq_matrix, 0)

    # --- 8. Compute the Euclidean distance matrix ---
    # Resulting shape: (N, N)
    dist_matrix = np.sqrt(dist_sq_matrix)

    # --- 9. Sum all pairwise distances ---
    total_dist = np.sum(dist_matrix)

    # --- 10. Print the result in the specified format ---
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == "__main__":
    # Example to create a dummy 'vectors.npy' for testing purposes.
    # In a real scenario, this part would be removed, and 'vectors.npy'
    # would be provided externally.
    if not os.path.exists('vectors.npy'):
        print("Creating a dummy 'vectors.npy' for demonstration...", file=sys.stderr)
        dummy_vectors = np.random.rand(8000, 1024).astype(np.float32)
        np.save('vectors.npy', dummy_vectors)
        print("Dummy 'vectors.npy' created. Running calculation...", file=sys.stderr)
    
    main()