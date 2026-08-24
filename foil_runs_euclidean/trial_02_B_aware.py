import numpy as np

def main():
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of 'vectors.npy' and prints the result.
    """
    # Load the matrix from 'vectors.npy'.
    # The problem statement implies this file will be present in the execution environment.
    try:
        V = np.load('vectors.npy')
    except FileNotFoundError:
        print("Error: 'vectors.npy' not found in the current directory.")
        print("Please ensure the matrix file is available for processing.")
        return

    # Validate matrix dimensions and data type.
    # The problem specifies an 8,000 x 1,024 float32 matrix.
    expected_shape = (8000, 1024)
    if V.shape != expected_shape:
        print(f"Warning: Expected matrix shape {expected_shape}, but loaded matrix has shape {V.shape}.")
    
    # Ensure the matrix is float32 as specified. Convert if necessary.
    # This conversion might create a temporary copy if the dtype is different,
    # but the original V will be released, keeping memory usage in check.
    if V.dtype != np.float32:
        print(f"Warning: Loaded matrix has dtype {V.dtype}, converting to float32.")
        V = V.astype(np.float32)

    N, D = V.shape

    # Initialize total_dist with float64 for higher precision accumulation.
    # Summing a large number of float32 values can lead to significant precision loss.
    total_dist = np.float64(0.0)

    # Iterate over each row v_i in the matrix V.
    # For each v_i, we calculate its Euclidean distance to all other rows v_j (including v_i itself).
    # This approach is memory-efficient as it avoids creating large N x N intermediate matrices.
    for i in range(N):
        v_i = V[i]  # Get the i-th row vector (shape: D,)

        # Calculate the difference between v_i and all rows in V.
        # (v_i - V) results in an (N, D) array of float32.
        # Immediately cast to float64 to perform subsequent calculations with higher precision.
        # Memory: V (31.25MB) + temp_f32 (31.25MB) + temp_f64 (62.5MB) = 125MB peak, within 128MB.
        diffs_f64 = (v_i - V).astype(np.float64)

        # Calculate the sum of squares of these differences along the dimension D.
        # This gives an (N,) array where each element is ||v_i - v_j||^2.
        sq_dists_i_f64 = np.sum(diffs_f64**2, axis=1)

        # Take the square root to get the Euclidean distances ||v_i - v_j||_2.
        # This results in an (N,) array of float64.
        dists_i_f64 = np.sqrt(sq_dists_i_f64)

        # Add the sum of these N distances to the running total.
        total_dist += np.sum(dists_i_f64)

    # Print the final result in the specified format.
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == "__main__":
    main()