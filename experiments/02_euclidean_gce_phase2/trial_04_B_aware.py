import numpy as np
import os
import sys

def main():
    """
    Calculates the total sum of all pairwise Euclidean distances between rows
    of 'vectors.npy' and prints the result.
    """

    # --- Helper function to create dummy data for local testing ---
    # This function will only create 'vectors.npy' if it doesn't already exist.
    # In a production environment where 'vectors.npy' is guaranteed to be present,
    # this function call can be safely removed or commented out.
    def create_dummy_vectors_file(filename='vectors.npy', N=8000, D=1024):
        if not os.path.exists(filename):
            print(f"Creating dummy '{filename}' for testing...", file=sys.stderr)
            # Use a fixed seed for reproducibility of dummy data
            np.random.seed(42)
            dummy_vectors = np.random.rand(N, D).astype(np.float32)
            np.save(filename, dummy_vectors)
            print(f"Dummy '{filename}' created with shape {dummy_vectors.shape}.", file=sys.stderr)

    # Call the dummy data creation function
    create_dummy_vectors_file()
    # --- End of dummy data creation ---

    # Load the vectors from 'vectors.npy'
    try:
        vectors = np.load('vectors.npy')
    except FileNotFoundError:
        print("Error: 'vectors.npy' not found. Please ensure the file exists.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading 'vectors.npy': {e}", file=sys.stderr)
        sys.exit(1)

    N, D = vectors.shape

    # Validate data type and dimensions
    if vectors.dtype != np.float32:
        print(f"Warning: 'vectors.npy' has dtype {vectors.dtype}, expected float32. Converting...", file=sys.stderr)
        vectors = vectors.astype(np.float32)

    if N != 8000 or D != 1024:
        print(f"Warning: 'vectors.npy' has shape {vectors.shape}, expected (8000, 1024). "
              "Proceeding with given dimensions.", file=sys.stderr)

    # Initialize the sum of distances for i < j pairs
    total_distance_sum_i_lt_j = 0.0

    # Iterate through each vector v_i
    for i in range(N):
        v_i = vectors[i]
        
        # Get the slice of vectors from index i+1 to N-1.
        # This slice represents v_j for j > i.
        # V_rest is a view into the original 'vectors' array, so it doesn't
        # consume additional memory for the data itself.
        V_rest = vectors[i+1:] 
        
        # Only proceed if there are vectors remaining to compare against
        if V_rest.shape[0] > 0:
            # Calculate the difference between v_i and all vectors in V_rest.
            # v_i is (D,), V_rest is (M, D), where M = N - 1 - i.
            # NumPy's broadcasting handles this efficiently, resulting in a (M, D) array.
            # This 'diffs' array is a temporary allocation. Max size: (N-1) * D * 4 bytes (~31.25 MB).
            diffs = v_i - V_rest
            
            # Square the differences element-wise.
            # This 'squared_diffs' array is another temporary allocation. Max size: (~31.25 MB).
            squared_diffs = diffs**2
            
            # Sum the squared differences along the feature dimension (axis=1)
            # to get the squared Euclidean distance for each pair (v_i, v_j).
            # This 'squared_distances' array is temporary. Max size: (N-1) * 4 bytes (~32 KB).
            squared_distances = np.sum(squared_diffs, axis=1)
            
            # Take the square root to get the Euclidean distances.
            # This 'distances' array is temporary. Max size: (~32 KB).
            distances = np.sqrt(squared_distances)
            
            # Add the sum of these distances to the running total.
            total_distance_sum_i_lt_j += np.sum(distances)

    # The problem asks for sum_{i,j} ||v_i - v_j||_2.
    # Our loop calculated sum_{i<j} ||v_i - v_j||_2.
    # Since ||v_i - v_j||_2 = ||v_j - v_i||_2, and ||v_i - v_i||_2 = 0,
    # the total sum is 2 * (sum_{i<j} ||v_i - v_j||_2).
    final_total_distance = 2 * total_distance_sum_i_lt_j

    # Print the result in the specified format
    print(f"TOTAL_DIST:{final_total_distance}")

if __name__ == "__main__":
    main()