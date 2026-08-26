import numpy as np

def main():
    X = np.load('vectors.npy')
    N, D = X.shape
    
    # Precompute squared L2 norms for each row
    sq_norms = np.einsum('ij,ij->i', X, X)
    
    total_dist = 0.0
    block_size = 1000
    
    for i in range(0, N, block_size):
        i_end = min(i + block_size, N)
        X_i = X[i:i_end]
        sq_i = sq_norms[i:i_end, None]
        
        for j in range(i, N, block_size):
            j_end = min(j + block_size, N)
            X_j = X[j:j_end]
            sq_j = sq_norms[None, j:j_end]
            
            # Gram matrix block: (i_end - i) x (j_end - j)
            dot = np.matmul(X_i, X_j.T)
            
            # dist_sq = ||x_i||^2 + ||x_j||^2 - 2 * <x_i, x_j>
            dist_sq = sq_i + sq_j - 2.0 * dot
            np.maximum(dist_sq, 0.0, out=dist_sq)
            np.sqrt(dist_sq, out=dist_sq)
            
            if i == j:
                total_dist += np.sum(np.triu(dist_sq, k=1), dtype=np.float64)
            else:
                total_dist += np.sum(dist_sq, dtype=np.float64)
                
    full_sum = 2.0 * total_dist
    print(f"TOTAL_DIST:{full_sum}")

if __name__ == '__main__':
    main()
