import numpy as np
import os
import sys

# --- Dummy 'vectors.npy' creation for local testing ---
# This block will create a dummy 'vectors.npy' if it doesn't exist.
# In the actual execution environment, 'vectors.npy' is expected to be provided.
# For submission, this block can be removed or commented out.
if not os.path.exists('vectors.npy'):
    print("Creating a dummy 'vectors.npy' for demonstration purposes.", file=sys.stderr)
    N_full = 8000
    D_full = 1024
    print(f"Generating a large dummy 'vectors.npy' with shape ({N_full}, {D_full}) and float32 type...", file=sys.stderr)
    # Generate random data. np.random.rand creates float64 by default,
    # then converting to float32. The temporary float64 array (65.5 MB)
    # plus the final float32 array (32.7 MB) fits within 128 MB during creation.
    dummy_vectors_full = np.random.rand(N_full, D_full).astype(np.float32)
    np.save('vectors.npy', dummy_vectors_full)
    print(f"Dummy 'vectors.npy' created successfully.", file=sys.stderr)
# --- End of dummy file creation ---

def calculate_pairwise_euclidean_distances_sum(file_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix stored in a .npy file.

    Args:
        file_path (str): The path to the .npy file containing the matrix.

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

    # Ensure the data type is float32 as specified, converting if necessary.
    # This is important for memory consistency and numerical precision.
    if vectors.dtype != np.float32:
        print(f"Warning: 'vectors.npy' has dtype {vectors.dtype}, converting to float32.", file=sys.stderr)
        vectors = vectors.astype(np.float32)

    N, D = vectors.shape
    # print(f"Loaded vectors with shape: {vectors.shape} and dtype: {vectors.dtype}", file=sys.stderr)

    total_distance = 0.0

    # Iterate over each row (vector v_i) in the matrix.
    # For each v_i, calculate its Euclidean distance to all other vectors v_j
    # (including itself, where distance is 0).
    # This approach is memory-efficient as it avoids creating a full N x N distance matrix.
    for i in range(N):
        # Get the current vector v_i. This is a view, not a copy.
        v_i = vectors[i]

        # Calculate the difference between v_i and all vectors in the matrix.
        # v_i is (D,), vectors is (N, D). Broadcasting results in an (N, D) array.
        # Memory: N * D * sizeof(float32) = 8000 * 1024 * 4 bytes = 32.768 MB
        diffs = v_i - vectors

        # Square the differences.
        # Memory: Another N * D * sizeof(float32) = 32.768 MB.
        # NumPy might optimize memory reuse here, but worst case is two such arrays.
        sq_diffs = diffs**2

        # Sum the squared differences along the feature dimension (axis=1).
        # This gives an (N,) array where each element is ||v_i - v_j||_2^2.
        # Memory: N * sizeof(float32) = 8000 * 4 bytes = 32 KB.
        sum_sq_diffs = np.sum(sq_diffs, axis=1)

        # Take the square root to get the Euclidean distances ||v_i - v_j||_2.
        # Memory: N * sizeof(float32) = 32 KB.
        distances = np.sqrt(sum_sq_diffs)

        # Add the sum of these distances (from v_i to all v_j) to the total.
        total_distance += np.sum(distances)

    return total_distance

if __name__ == "__main__":
    result = calculate_pairwise_euclidean_distances_sum()
    print(f"TOTAL_DIST:{result}")