import numpy as np

def main():
    filename = 'vectors.npy'

    # 1. Load the matrix from the .npy file
    try:
        vectors = np.load(filename)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        print("Please ensure 'vectors.npy' is in the same directory as the script.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while loading '{filename}': {e}")
        return

    # Verify the shape and data type of the loaded matrix (optional, but good practice)
    expected_shape = (8000, 1024)
    expected_dtype = np.float32
    if vectors.shape != expected_shape or vectors.dtype != expected_dtype:
        print(f"Warning: Loaded matrix has shape {vectors.shape} and dtype {vectors.dtype}.")
        print(f"Expected shape {expected_shape} and dtype {expected_dtype}.")
        # The script will proceed with the loaded data, but this warning might be useful.

    # 2. Compute the sum of each column
    # np.sum(vectors, axis=0) sums elements along the rows (axis 0),
    # resulting in a 1D array where each element is the sum of a column.
    column_sums = np.sum(vectors, axis=0)

    # 3. Square each of these column sums
    squared_column_sums = column_sums**2

    # 4. Sum all the squared column sums to get the total sum of all pairwise dot products
    total_sum = np.sum(squared_column_sums)

    # 5. Print the result in the specified format
    print(f"TOTAL_SUM:{total_sum}")

if __name__ == "__main__":
    main()