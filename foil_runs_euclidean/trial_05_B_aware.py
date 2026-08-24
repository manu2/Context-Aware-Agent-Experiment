import numpy as np
import sys
import os

def main():
    # --- File Loading and Error Handling ---
    # This block handles loading 'vectors.npy'.
    # For local testing, if 'vectors.npy' doesn't exist, a dummy file is created.
    # In the actual execution environment, this file will be provided.
    if not os.path.exists('vectors.npy'):
        print("Creating dummy vectors.npy for testing...", file=sys.stderr)
        # Use a fixed seed for reproducibility of dummy data
        np.random.seed(42)
        dummy_vectors = np.random.rand(8000, 1024).astype(np.float32)
        np.save('vectors.npy', dummy_vectors)
        print("Dummy vectors.npy created.", file=sys.stderr)

    try:
        V = np.load('vectors.npy')
    except FileNotFoundError:
        print("Error: vectors.npy not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading vectors.npy: {e}", file=sys.stderr)
        sys.exit(1)

    N, D = V.shape

    # --- Edge Case: Empty Matrix ---
    # If the matrix has no rows, the total distance is 0.
    if N == 0:
        print("TOTAL_DIST:0.0")
        sys.exit(0)

    # --- Core Calculation Logic ---
    # Initialize total_distance as a float64 to maintain precision during accumulation.
    total_distance = 0.0

    # The problem asks for sum_{i,j} ||v_i - v_j||_2.
    # We can optimize this by calculating sum_{i<j} ||v_i - v_j||_2 and then multiplying by 2.
    # This is because ||v_i - v_j||_2 = ||v_j - v_i||_2 (symmetry)
    # and ||v_i - v_i||_2 = 0 (diagonal elements).
    # So, sum_{i,j} ||v_i - v_j||_2 = 2 * sum_{i<j} ||v_i - v_j||_2.

    for i in range(N):
        # For each vector v_i, calculate its Euclidean distance to all subsequent vectors v_j (where j > i).
        # This approach ensures that temporary memory allocations are kept within limits.
        if i + 1 < N: # Ensure there are vectors remaining for j > i
            v_i = V[i] # Current vector (a view into V, no extra memory)
            V_remaining = V[i+1:] # Remaining vectors (a view into V, no extra memory)

            # Calculate the element-wise difference between v_i and all vectors in V_remaining.
            # v_i (shape D,) is broadcasted to (1, D) and subtracted from V_remaining (shape N-i-1, D).
            # 'diffs' will be a temporary array of shape (N-i-1, D).
            diffs = v_i - V_remaining

            # Square each element of the differences.
            # 'sq_diffs' will be another temporary array of shape (N-i-1, D).
            sq_diffs = diffs * diffs # Element-wise multiplication is often slightly faster than **2

            # Sum the squared differences along the feature dimension (axis=1).
            # This results in an array of squared Euclidean distances, shape (N-i-1,).
            sum_sq_diffs = np.sum(sq_diffs, axis=1)

            # Take the square root to get the actual Euclidean distances.
            # 'distances' will be an array of shape (N-i-1,).
            distances = np.sqrt(sum_sq_diffs)

            # Add the sum of these distances to the running total.
            total_distance += distances.sum() # .sum() method is often slightly faster than np.sum()

    # Multiply the accumulated sum by 2 to account for symmetric pairs (i,j) and (j,i).
    # The diagonal elements (i=j) are zero and thus don't contribute to the sum.
    final_total_distance = 2 * total_distance

    # --- Output Result ---
    print(f"TOTAL_DIST:{final_total_distance}")

# Ensure the main function is called only when the script is executed directly.
if __name__ == "__main__":
    main()