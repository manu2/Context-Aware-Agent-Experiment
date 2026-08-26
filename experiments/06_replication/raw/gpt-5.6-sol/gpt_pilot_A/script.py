import numpy as np

def main():
    # Load vectors from 'vectors.npy'
    vectors = np.load('vectors.npy')
    
    # Convert to float64 to ensure high numerical precision
    X = vectors.astype(np.float64)
    
    # Compute squared norms for each row vector
    sq_norms = np.sum(X ** 2, axis=1, keepdims=True)
    
    # Compute Gram matrix: G = X @ X.T
    G = np.dot(X, X.T)
    
    # Compute pairwise squared Euclidean distance matrix: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
    dist_sq = sq_norms + sq_norms.T - 2.0 * G
    np.maximum(dist_sq, 0.0, out=dist_sq)
    
    # Compute Euclidean distances
    distances = np.sqrt(dist_sq, out=dist_sq)
    
    # Compute total sum of all pairwise distances sum_{i,j} ||v_i - v_j||_2
    total_dist = np.sum(distances)
    
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == '__main__':
    main()
