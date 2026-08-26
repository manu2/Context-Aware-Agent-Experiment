import numpy as np

def compute_total_pairwise_distance(file_path='vectors.npy'):
    # Load the matrix (8000 x 1024 float32)
    vectors = np.load(file_path)
    
    # Cast to float64 to ensure high numerical precision
    v = np.asarray(vectors, dtype=np.float64)
    
    # Compute squared Euclidean norms: ||v_i||^2 (shape: 8000 x 1)
    sq_norms = np.sum(v ** 2, axis=1, keepdims=True)
    
    # Pairwise squared distances: ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * <v_i, v_j>
    # Gram matrix: G = V @ V.T (8000 x 8000)
    dist_sq = sq_norms + sq_norms.T - 2.0 * np.dot(v, v.T)
    
    # Clip negative values resulting from numerical precision errors
    np.maximum(dist_sq, 0.0, out=dist_sq)
    np.fill_diagonal(dist_sq, 0.0)
    
    # Euclidean distance
    dist = np.sqrt(dist_sq)
    
    # Total sum of all pairwise distances
    total_dist = np.sum(dist)
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == '__main__':
    compute_total_pairwise_distance('vectors.npy')
