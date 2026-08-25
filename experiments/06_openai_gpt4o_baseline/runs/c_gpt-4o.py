import numpy as np

def compute_total_pairwise_distance(matrix):
    # Calculate the squared norms of each row
    squared_norms = np.sum(matrix ** 2, axis=1)
    
    # Compute the pairwise squared Euclidean distances using the identity:
    # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * v_i . v_j
    pairwise_squared_distances = (
        squared_norms[:, np.newaxis] + squared_norms[np.newaxis, :] - 2 * np.dot(matrix, matrix.T)
    )
    
    # Sum all pairwise distances (take the square root of squared distances)
    total_distance = np.sum(np.sqrt(pairwise_squared_distances))
    
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