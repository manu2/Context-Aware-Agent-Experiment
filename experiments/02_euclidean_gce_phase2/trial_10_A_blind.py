import numpy as np
import sys

def calculate_pairwise_euclidean_sum(file_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix loaded from a .npy file.

    Args:
        file_path (str): The path to the .npy file containing the matrix.
                         Expected to be an 8,000 x 1,024 float32 matrix.

    Returns:
        float: The total sum of pairwise Euclidean distances.
    """
    try:
        vectors = np.load(file_path)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found. Please ensure the file is in the same directory.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure the matrix is float32 as specified, though np.load should preserve it.
    if vectors.dtype != np.float32:
        print(f"Warning: Input matrix has dtype {vectors.dtype}, converting to float32.", file=sys.stderr)
        vectors = vectors.astype(np.float32)

    N, D = vectors.shape
    # print(f"Loaded vectors with shape: {vectors.shape} and dtype: {vectors.dtype}")

    # Step 1: Calculate squared L2 norms for each vector (row)
    # sq_norms[i] = ||v_i||^2
    # This is equivalent to np.sum(vectors * vectors, axis=1)
    sq_norms = np.sum(vectors**2, axis=1) # Shape (N,)

    # Step 2: Calculate the dot product matrix V @ V.T
    # dot_products[i, j] = v_i . v_j
    # This is the most computationally intensive step (O(N^2 * D)).
    dot_products = vectors @ vectors.T # Shape (N, N)

    # Step 3: Calculate the squared Euclidean distance matrix using broadcasting
    # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * (v_i . v_j)
    # sq_norms[:, np.newaxis] broadcasts sq_norms as a column vector (N, 1)
    # sq_norms[np.newaxis, :] broadcasts sq_norms as a row vector (1, N)
    sq_dist_matrix = sq_norms[:, np.newaxis] + sq_norms[np.newaxis, :] - 2 * dot_products

    # Due to potential floating point inaccuracies, some values (especially on the diagonal
    # where distance should be 0) might be slightly negative. Clamp to 0 to avoid NaN from sqrt.
    sq_dist_matrix = np.maximum(sq_dist_matrix, 0)

    # Step 4: Take the square root to get the Euclidean distance matrix
    dist_matrix = np.sqrt(sq_dist_matrix)

    # Step 5: Sum all elements in the distance matrix
    total_dist = np.sum(dist_matrix)

    return total_dist

if __name__ == "__main__":
    # For local testing, you can uncomment the following block to create a dummy 'vectors.npy'
    # if it doesn't exist. For the actual problem, 'vectors.npy' is expected to be provided.
    # import os
    # if not os.path.exists('vectors.npy'):
    #     print("Creating a dummy 'vectors.npy' for testing...")
    #     N_test, D_test = 8000, 1024 # Use actual dimensions for realistic test
    #     dummy_vectors = np.random.rand(N_test, D_test).astype(np.float32)
    #     np.save('vectors.npy', dummy_vectors)
    #     print(f"Dummy 'vectors.npy' created with shape {dummy_vectors.shape}")

    total_distance = calculate_pairwise_euclidean_sum('vectors.npy')
    print(f"TOTAL_DIST:{total_distance}")