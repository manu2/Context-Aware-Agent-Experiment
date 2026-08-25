import numpy as np
import sys # Used for sys.exit in case of errors

def calculate_total_pairwise_euclidean_distance(vectors_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix loaded from a .npy file.

    Args:
        vectors_path (str): The path to the .npy file containing the matrix.
                            Expected to be an 8000 x 1024 float32 matrix.

    Returns:
        float: The total sum of all pairwise Euclidean distances.
    """
    try:
        V = np.load(vectors_path)
    except FileNotFoundError:
        print(f"Error: '{vectors_path}' not found. Please ensure the file exists in the same directory.")
        raise # Re-raise the error to be caught by the main block for graceful exit.
    except Exception as e:
        print(f"Error loading '{vectors_path}': {e}")
        raise # Re-raise any other loading errors.

    # Ensure the matrix is float32 as specified.
    # If the input is not float32, convert it to maintain consistent precision.
    if V.dtype != np.float32:
        V = V.astype(np.float32)

    # N = number of vectors (rows), D = dimension of each vector (columns)
    # V.shape will be (N, D)
    
    # Step 1: Compute squared L2 norms for each row vector: ||v_i||^2
    # This is sum(v_ik^2) for each i, resulting in a vector of shape (N,)
    # Example: for v = [x, y], ||v||^2 = x^2 + y^2
    row_norms_sq = np.sum(V**2, axis=1)

    # Step 2: Compute the dot product matrix: V @ V.T
    # This matrix (M) has M[i,j] = v_i . v_j, resulting in an (N, N) matrix
    # This is the most computationally intensive step, but highly optimized by NumPy.
    dot_products = V @ V.T

    # Step 3: Compute the pairwise squared Euclidean distances using the identity:
    # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * (v_i . v_j)
    #
    # row_norms_sq[:, np.newaxis] reshapes the (N,) vector to (N, 1) (column vector)
    # row_norms_sq[np.newaxis, :] reshapes the (N,) vector to (1, N) (row vector)
    #
    # When these are added, NumPy's broadcasting rules create an (N, N) matrix
    # where element (i,j) is ||v_i||^2 + ||v_j||^2.
    dist_sq = row_norms_sq[:, np.newaxis] + row_norms_sq[np.newaxis, :] - 2 * dot_products

    # Step 4: Handle potential floating point inaccuracies.
    # Due to precision errors, dist_sq might contain very small negative values
    # (e.g., -1e-7 for diagonal elements that should be 0).
    # np.sqrt(negative) would result in NaN. Clamp values to 0 to prevent this.
    dist_sq = np.maximum(dist_sq, 0)

    # Step 5: Compute the actual Euclidean distances by taking the square root.
    # The result is an (N, N) matrix of float32 distances.
    distances = np.sqrt(dist_sq)

    # Step 6: Sum all pairwise distances.
    # This sums all N*N elements of the distances matrix.
    total_dist = np.sum(distances)

    return total_dist

if __name__ == "__main__":
    vectors_file = 'vectors.npy'
    try:
        total_distance = calculate_total_pairwise_euclidean_distance(vectors_file)
        # Step 7: Print the result in the specified format.
        print(f"TOTAL_DIST:{total_distance}")
    except Exception as e:
        # An error message would have been printed by the function.
        # Exit with a non-zero status code to indicate failure.
        sys.exit(1)