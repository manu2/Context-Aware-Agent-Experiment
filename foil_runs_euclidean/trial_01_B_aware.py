import numpy as np

def calculate_total_pairwise_euclidean_distance(vectors_path='vectors.npy'):
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of a matrix stored in a .npy file.

    Args:
        vectors_path (str): The path to the .npy file containing the matrix.
                            Expected format: (N, D) float32 numpy array.
    """
    # Load the matrix from the .npy file.
    # If 'vectors.npy' is not found, np.load will raise a FileNotFoundError.
    vectors = np.load(vectors_path)

    N, D = vectors.shape

    # Ensure data type is float32 as specified.
    # This conversion is a safeguard; ideally, the input file is already float32.
    if vectors.dtype != np.float32:
        # print(f"Warning: Input matrix dtype is {vectors.dtype}, converting to float32.")
        vectors = vectors.astype(np.float32)

    total_distance = 0.0

    # Iterate through each row (v_i) of the matrix.
    # For each v_i, calculate its Euclidean distance to all other rows (v_j).
    # This approach uses broadcasting to compute N distances in each iteration,
    # keeping memory usage within the specified limits.
    for i in range(N):
        v_i = vectors[i] # This is a (D,) array, typically a view into `vectors`.

        # Calculate differences between v_i and all vectors in `vectors`.
        # `v_i` (D,) is broadcast against `vectors` (N, D) to produce `diffs` (N, D).
        diffs = v_i - vectors

        # Square the differences element-wise. `sq_diffs` is (N, D).
        sq_diffs = diffs * diffs

        # Sum the squared differences along the feature dimension (axis=1).
        # This results in an (N,) array, where each element is sum_k (v_i[k] - v_j[k])^2.
        sum_sq_diffs = np.sum(sq_diffs, axis=1)

        # Take the square root to get the Euclidean distances.
        # `distances_from_vi` is an (N,) array of ||v_i - v_j||_2 for all j.
        distances_from_vi = np.sqrt(sum_sq_diffs)

        # Add the sum of these distances to the total.
        # `total_distance` is a float64 (Python's default float), ensuring precision for the large sum.
        total_distance += np.sum(distances_from_vi)

    print(f"TOTAL_DIST:{total_distance}")

if __name__ == "__main__":
    # To run this script:
    # 1. Make sure you have numpy installed (`pip install numpy`).
    # 2. Ensure your 'vectors.npy' file (an 8000x1024 float32 matrix)
    #    is in the same directory as this script, or provide its full path.
    # 3. Execute the script: `python your_script_name.py`

    # Example of how to create a 'vectors.npy' for testing (uncomment to run):
    # N_test = 8000
    # D_test = 1024
    # # Using a fixed seed for reproducibility of test data
    # np.random.seed(42)
    # test_vectors = np.random.rand(N_test, D_test).astype(np.float32) * 100 # Scale values for more varied distances
    # np.save('vectors.npy', test_vectors)
    # print(f"Created 'vectors.npy' with shape {test_vectors.shape} for testing.")

    calculate_total_pairwise_euclidean_distance()