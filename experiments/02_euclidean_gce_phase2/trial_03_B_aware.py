import numpy as np
import os
import sys

def main():
    # Define matrix dimensions and data type as per problem statement
    N_ROWS = 8000
    N_COLS = 1024
    DTYPE = np.float32
    FILENAME = 'vectors.npy'

    # --- Create a dummy 'vectors.npy' for testing if it doesn't exist ---
    # This block makes the script self-contained and runnable out-of-the-box.
    # If 'vectors.npy' is provided, it will be used. Otherwise, a dummy file
    # matching the specified dimensions and dtype will be generated.
    if not os.path.exists(FILENAME):
        print(f"'{FILENAME}' not found. Creating a dummy file for demonstration purposes...")
        try:
            # Generate random data (values between 0 and 1)
            V_dummy = np.random.rand(N_ROWS, N_COLS).astype(DTYPE)
            np.save(FILENAME, V_dummy)
            print(f"Dummy '{FILENAME}' created with shape {V_dummy.shape} and dtype {V_dummy.dtype}.")
        except Exception as e:
            print(f"Error creating dummy '{FILENAME}': {e}")
            sys.exit(1) # Exit if dummy file creation fails

    # --- Load the vectors matrix ---
    try:
        vectors = np.load(FILENAME)
    except FileNotFoundError:
        # This case should ideally not be hit if the dummy creation works,
        # but it's good for robustness in case of file system issues.
        print(f"Error: '{FILENAME}' not found. Please ensure the file is in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading '{FILENAME}': {e}")
        sys.exit(1)

    # Validate loaded matrix properties against problem specifications
    if vectors.shape != (N_ROWS, N_COLS) or vectors.dtype != DTYPE:
        print(f"Warning: Loaded '{FILENAME}' has unexpected shape {vectors.shape} or dtype {vectors.dtype}.")
        print(f"Expected shape: ({N_ROWS}, {N_COLS}), Expected dtype: {DTYPE}.")
        # The script will proceed with the loaded data, but this warning is important.
        # If strict adherence to dimensions is required, uncomment sys.exit(1) here.
        # sys.exit(1)

    N, D = vectors.shape
    print(f"Processing matrix with shape: {vectors.shape}, dtype: {vectors.dtype}")

    # Initialize total_dist as a float64 to maintain precision during accumulation
    total_dist = 0.0

    # --- Compute total sum of pairwise Euclidean distances ---
    # This loop iterates through each vector v_i and calculates its Euclidean
    # distance to all other vectors v_j. This approach avoids creating a large
    # N x N distance matrix, which would exceed the memory limit.
    for i in range(N):
        # Calculate the difference between the current vector v_i and all other vectors v_j.
        # `vectors[i]` is a (D,) array (the i-th row).
        # `vectors` is an (N, D) array.
        # The subtraction `vectors[i] - vectors` uses NumPy's broadcasting rules.
        # It effectively subtracts `vectors[i]` from each row of `vectors`,
        # resulting in an (N, D) array where each row `k` is `v_i - v_k`.
        diffs = vectors[i] - vectors

        # Square the differences element-wise.
        # This results in an (N, D) array of squared differences.
        sq_diffs = diffs**2

        # Sum the squared differences along the feature dimension (axis=1).
        # This gives an (N,) array where each element `k` is ||v_i - v_k||_2^2.
        sum_sq_diffs = np.sum(sq_diffs, axis=1)

        # Take the square root to get the Euclidean distances.
        # This results in an (N,) array where each element `k` is ||v_i - v_k||_2.
        distances = np.sqrt(sum_sq_diffs)

        # Add the sum of these N distances to the total accumulator.
        # `np.sum(distances)` will be float32, but adding to `total_dist` (float64)
        # promotes it to float64, preserving overall precision.
        total_dist += np.sum(distances)

    # --- Print the final result in the specified format ---
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == "__main__":
    main()