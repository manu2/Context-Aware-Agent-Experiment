import numpy as np

def main():
    vectors = np.load('vectors.npy')
    vectors = vectors.astype(np.float64)
    
    # Compute squared L2 norms of each vector: shape (N,)
    sq_norms = np.sum(vectors ** 2, axis=1)
    
    # Compute pairwise squared Euclidean distances using:
    # ||v_i - v_j||^2 = ||v_i||^2 + ||v_j||^2 - 2 * <v_i, v_j>
    # Using batching to be memory-efficient and cache-friendly
    n_rows = vectors.shape[0]
    batch_size = 1000
    total_dist = 0.0
    
    for start_idx in range(0, n_rows, batch_size):
        end_idx = min(start_idx + batch_size, n_rows)
        batch = vectors[start_idx:end_idx]
        
        # Compute dot products for the batch: shape (batch_len, n_rows)
        dot_products = np.dot(batch, vectors.T)
        
        # Compute squared distances
        dists_sq = sq_norms[start_idx:end_idx, np.newaxis] + sq_norms[np.newaxis, :] - 2.0 * dot_products
        
        # Numerical cleanup: clamp negatives to 0.0 and zero out diagonal
        np.maximum(dists_sq, 0.0, out=dists_sq)
        for i in range(end_idx - start_idx):
            dists_sq[i, start_idx + i] = 0.0
            
        # Euclidean distance
        dists = np.sqrt(dists_sq)
        total_dist += np.sum(dists)
        
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == '__main__':
    main()
