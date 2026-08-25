import numpy as np

def compute_total_pairwise_distance(matrix):
    # Calculate the squared Euclidean distance using the identity:
    # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * v_i . v_j
    # where v_i . v_j is the dot product of v_i and v_j

    # Compute the squared norms of each row vector
    squared_norms = np.sum(matrix ** 2, axis=1)

    # Compute the dot product matrix
    dot_product_matrix = np.dot(matrix, matrix.T)

    # Calculate the squared pairwise distances
    squared_distances = squared_norms[:, np.newaxis] + squared_norms[np.newaxis, :] - 2 * dot_product_matrix

    # Since distances are symmetric, we only need to sum the upper triangle (excluding diagonal)
    total_distance = np.sum(np.sqrt(squared_distances[np.triu_indices_from(squared_distances, k=1)]))

    return total_distance

def main():
    # Load the matrix from the 'vectors.npy' file
    matrix = np.load('vectors.npy')

    # Compute the total sum of all pairwise Euclidean distances
    total_distance = compute_total_pairwise_distance(matrix)

    # Print the result
    print(f'TOTAL_DIST:{total_distance}')

if __name__ == '__main__':
    main()