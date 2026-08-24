import numpy as np
import sys
import os

def main():
    # --- Input File Check ---
    input_filename = 'vectors.npy'
    if not os.path.exists(input_filename):
        print(f"Error: '{input_filename}' not found in the current directory.", file=sys.stderr)
        sys.exit(1)

    # --- Load Data ---
    try:
        V = np.load(input_filename)
    except Exception as e:
        print(f"Error loading '{input_filename}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- Validate Matrix Properties ---
    expected_shape = (8000, 1024)
    expected_dtype = np.float32

    if V.shape != expected_shape:
        print(f"Warning: '{input_filename}' has shape {V.shape}, expected {expected_shape}.", file=sys.stderr)
    if V.dtype != expected_dtype:
        print(f"Warning: '{input_filename}' has dtype {V.dtype}, expected {expected_dtype}.", file=sys.stderr)

    N, D = V.shape
    total_dist = 0.0

    # --- Calculate Total Pairwise Euclidean Distance ---
    # The problem asks for sum_{i,j} ||v_i - v_j||_2.
    # This includes terms where i=j (which are 0) and counts each pair (i,j) and (j,i) separately.
    # The loop structure below naturally computes this sum.
    
    # Iterate over each vector V_i in the matrix
    for i in range(N):
        # Compute the difference between V[i] and all other vectors V[j] in the matrix V.
        # V[i] is a (D,) vector. V is an (N, D) matrix.
        # NumPy's broadcasting rules handle this: V[i] is treated as an (N, D) array
        # where each row is V[i], then element-wise subtraction occurs.
        # The result `diffs` is an (N, D) array, where `diffs[j, :] = V[i] - V[j]`.
        diffs = V[i] - V
        
        # Compute the Euclidean norm (L2 norm) for each row of `diffs`.
        # This results in an (N,) array of distances:
        # [||V[i] - V[0]||_2, ||V[i] - V[1]||_2, ..., ||V[i] - V[N-1]||_2]
        distances = np.linalg.norm(diffs, axis=1)
        
        # Add the sum of these N distances to the running total.
        total_dist += np.sum(distances)

    # --- Print Result ---
    # The output format is 'TOTAL_DIST:<value>'
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == '__main__':
    main()