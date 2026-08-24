import numpy as np
import os

def calculate_pairwise_dot_product_sum(file_path='vectors.npy'):
    """
    Loads a matrix from a .npy file, computes the total sum of all pairwise
    row dot products, and prints the result.

    Args:
        file_path (str): The path to the .npy file containing the matrix.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.", file=sys.stderr)
        # Optionally, create a dummy file for testing if needed
        # print("Creating a dummy 'vectors.npy' for demonstration...", file=sys.stderr)
        # dummy_vectors = np.random.rand(8000, 1024).astype(np.float32)
        # np.save(file_path, dummy_vectors)
        # print("Dummy file created. Please re-run the script.", file=sys.stderr)
        sys.exit(1)

    # Load the matrix from the .npy file
    # This will load the 8000x1024 float32 matrix into memory.
    # Memory usage: 8000 * 1024 * 4 bytes = ~31.25 MB
    vectors = np.load(file_path)

    # Compute the sum of all rows.
    # This results in a single vector of shape (1024,).
    # Memory usage: 1024 * 4 bytes = ~4 KB (negligible)
    sum_of_rows = vectors.sum(axis=0)

    # Compute the dot product of the sum_of_rows vector with itself.
    # This is mathematically equivalent to the sum of all pairwise row dot products.
    # np.dot might promote float32 to float64 for higher precision in the result.
    total_sum = np.dot(sum_of_rows, sum_of_rows)

    # Print the result in the specified format
    print(f"TOTAL_SUM:{total_sum}")

if __name__ == "__main__":
    import sys
    # Ensure numpy is available
    try:
        import numpy as np
    except ImportError:
        print("Error: NumPy is not installed. Please install it using 'pip install numpy'.", file=sys.stderr)
        sys.exit(1)

    calculate_pairwise_dot_product_sum('vectors.npy')