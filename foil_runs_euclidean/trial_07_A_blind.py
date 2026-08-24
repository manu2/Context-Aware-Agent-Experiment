import numpy as np
import os
import sys

def main():
    # Define matrix dimensions as per problem statement
    N_expected = 8000
    D_expected = 1024
    filename = 'vectors.npy'

    # --- Start: Code to generate dummy vectors.npy for testing if it doesn't exist ---
    # This block makes the script self-contained for demonstration and testing purposes.
    # In a production environment where 'vectors.npy' is guaranteed to be an input,
    # this block can be removed.
    if not os.path.exists(filename):
        print(f"'{filename}' not found. Generating a dummy file for demonstration.", file=sys.stderr)
        # Generate random float32 vectors
        # Using a fixed seed for reproducibility of the dummy file
        rng = np.random.default_rng(42)
        dummy_vectors = rng.random((N_expected, D_expected), dtype=np.float32)
        np.save(filename, dummy_vectors)
        print(f"Dummy '{filename}' with shape {dummy_vectors.shape} created.", file=sys.stderr)
    # --- End: Code to generate dummy vectors.npy ---

    # Load the vectors from the .npy file
    try:
        vectors = np.load(filename)
    except FileNotFoundError:
        print(f"Error: '{filename}' not found. Please ensure the file exists in the same directory.", file=sys.stderr)
        sys.exit(1) # Exit with an error code
    except Exception as e:
        print(f"Error loading '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

    # Validate the loaded data's shape and type
    if vectors.shape != (N_expected, D_expected) or vectors.dtype != np.float32:
        print(f"Error: '{filename}' has shape {vectors.shape} and dtype {vectors.dtype}, "
              f"expected ({N_expected}, {D_expected}) and float32.", file=sys.stderr)
        # If the input doesn't match the problem's specification, it's an error.
        sys.exit(1)

    # Calculate squared L2 norms for each vector
    # ||v_i||^2 = sum_k (v_i[k])^2
    # This will be a vector of shape (N,)
    sq_norms = np.sum(vectors**2, axis=1) # (N,)

    # Calculate the dot product matrix V @ V.T
    # This gives v_i . v_j for all pairs (i,j)
    # Resulting matrix will be (N, N)
    dot_products = vectors @ vectors.T # (N, D) @ (D, N) -> (N, N)

    # Calculate the squared Euclidean distance matrix D_sq[i,j] = ||v_i - v_j||^2
    # D_sq[i,j] = ||v_i||^2 - 2 * (v_i . v_j) + ||v_j||^2
    # Using broadcasting:
    # sq_norms[:, np.newaxis] is (N, 1)
    # sq_norms[np.newaxis, :] is (1, N)
    # The result will be (N, N)
    squared_distances = sq_norms[:, np.newaxis] - 2 * dot_products + sq_norms[np.newaxis, :]

    # Due to floating point inaccuracies, some values in squared_distances might be
    # very slightly negative (e.g., -1e-10) for distances that should be zero.
    # np.sqrt will produce NaNs for negative values.
    # We should clip these values to zero to prevent NaNs.
    squared_distances = np.maximum(squared_distances, 0)

    # Calculate the Euclidean distance matrix D[i,j] = ||v_i - v_j||_2
    # This will be (N, N)
    distances = np.sqrt(squared_distances)

    # Sum all pairwise distances
    # The problem asks for sum_{i,j} ||v_i - v_j||_2, which is the sum of all elements
    # in the 'distances' matrix.
    total_distance = np.sum(distances)

    # Print the result in the specified format
    print(f"TOTAL_DIST:{total_distance}")

if __name__ == "__main__":
    main()