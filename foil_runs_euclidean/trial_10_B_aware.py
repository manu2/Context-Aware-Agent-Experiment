import numpy as np
import sys
import os

def main():
    # Define the expected file name
    file_name = 'vectors.npy'

    # Check if the file exists
    if not os.path.exists(file_name):
        print(f"Error: '{file_name}' not found. Please ensure the file is in the same directory as the script.", file=sys.stderr)
        sys.exit(1)

    try:
        # Load the matrix from the .npy file
        # numpy.load handles the file format and memory mapping if needed,
        # but for this size, it will likely load into RAM directly.
        V = np.load(file_name)
    except Exception as e:
        print(f"Error loading '{file_name}': {e}", file=sys.stderr)
        sys.exit(1)

    # Validate the matrix dimensions and data type
    expected_shape = (8000, 1024)
    expected_dtype = np.float32

    if V.shape != expected_shape:
        print(f"Error: '{file_name}' has shape {V.shape}, but expected {expected_shape}.", file=sys.stderr)
        sys.exit(1)
    if V.dtype != expected_dtype:
        print(f"Warning: '{file_name}' has dtype {V.dtype}, but expected {expected_dtype}. Converting to float32.", file=sys.stderr)
        V = V.astype(expected_dtype)

    N = V.shape[0] # Number of vectors (rows)

    # Initialize the total sum of distances.
    # Using float64 for the sum to maintain precision over many additions.
    total_sum_distances = 0.0

    # Iterate through each vector V[i] in the matrix
    for i in range(N):
        # Calculate the difference between the current vector V[i] and all other vectors V[j].
        # V[i] is a (D,) vector. V is an (N, D) matrix.
        # NumPy's broadcasting rules apply: V[i] is treated as (1, D) and subtracted from each row of V.
        # The result `diffs` will be an (N, D) matrix, where diffs[j] = V[i] - V[j].
        diffs = V[i] - V
        
        # Calculate the Euclidean norm (L2 norm) for each row of `diffs`.
        # This computes ||V[i] - V[j]||_2 for all j from 0 to N-1.
        # The result `distances_from_Vi` is an (N,) array of distances.
        # np.linalg.norm typically returns float64 for float32 input, which is good for precision.
        distances_from_Vi = np.linalg.norm(diffs, axis=1)
        
        # Add the sum of these distances (from V[i] to all V[j]) to the running total.
        # This correctly accumulates sum_{j} ||V[i] - V[j]||_2 for the current i.
        total_sum_distances += np.sum(distances_from_Vi)

    # The problem asks for sum_{i,j} ||v_i - v_j||_2.
    # Our loop structure correctly computes this:
    # For each i, we sum ||V_i - V_j|| for all j.
    # Then we sum these results over all i.
    # This includes terms where i=j (which are 0) and counts (i,j) and (j,i) as distinct pairs.

    # Print the final result in the specified format.
    print(f"TOTAL_DIST:{total_sum_distances}")

if __name__ == "__main__":
    main()