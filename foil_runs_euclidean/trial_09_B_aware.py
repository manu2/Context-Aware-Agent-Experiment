import numpy as np
import sys
import os

def main():
    # Define the filename for the input matrix
    filename = 'vectors.npy'

    # Check if the input file exists
    if not os.path.exists(filename):
        print(f"Error: '{filename}' not found. Please ensure the file is in the same directory as the script.", file=sys.stderr)
        sys.exit(1)

    try:
        # Load the matrix from the .npy file.
        # The problem statement guarantees it's 8000x1024 float32.
        V = np.load(filename)
    except Exception as e:
        print(f"Error loading '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

    # Basic validation of matrix properties (optional, but good for robustness)
    if V.dtype != np.float32:
        print(f"Warning: Input matrix dtype is {V.dtype}, expected float32. This might affect memory usage or precision.", file=sys.stderr)
    if V.shape != (8000, 1024):
        print(f"Warning: Input matrix shape is {V.shape}, expected (8000, 1024).", file=sys.stderr)

    N, D = V.shape

    # Initialize total_dist as a float64 to ensure precision during summation.
    # Summing many float32 values can lead to significant precision loss.
    total_dist = 0.0

    # Iterate through each vector v_i in the matrix V.
    # For each v_i, we calculate its Euclidean distance to all other vectors v_j (including v_i itself).
    # This approach avoids creating a full N x N distance matrix, which would exceed memory limits.
    for i in range(N):
        # Calculate the difference between the current vector V[i] and all vectors in V.
        # V[i] is a (D,) vector. V is an (N, D) matrix.
        # NumPy's broadcasting rules apply: V[i] is effectively broadcasted to (N, D)
        # for element-wise subtraction with V.
        diffs = V[i] - V  # Resulting shape: (N, D)

        # Calculate the Euclidean norm (L2 norm) for each row in 'diffs'.
        # This computes an array of distances:
        # [||V[i]-V[0]||_2, ||V[i]-V[1]||_2, ..., ||V[i]-V[N-1]||_2]
        distances_from_vi = np.linalg.norm(diffs, axis=1) # Resulting shape: (N,)

        # Add the sum of these N distances to the running total.
        total_dist += np.sum(distances_from_vi)

    # Print the final result in the specified format.
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == "__main__":
    main()