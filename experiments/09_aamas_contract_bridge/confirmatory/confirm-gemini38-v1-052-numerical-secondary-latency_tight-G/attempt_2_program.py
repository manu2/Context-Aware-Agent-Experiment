import numpy as np

def main():
    # Load vectors as float64 for high numerical precision and stability
    X = np.load('vectors_secondary.npy').astype(np.float64)
    n = X.shape[0]
    
    # Precompute squared norms: ||x_i||^2
    sq = np.einsum('ij,ij->i', X, X)
    
    total = 0.0
    batch_size = 1000
    
    for i in range(0, n, batch_size):
        X_batch = X[i:i + batch_size]
        b_len = len(X_batch)
        sq_batch = sq[i:i + b_len]
        
        # ||u - v||^2 = ||u||^2 + ||v||^2 - 2 * <u, v>
        dist_sq = X_batch @ X.T
        dist_sq *= -2.0
        dist_sq += sq_batch[:, None]
        dist_sq += sq[None, :]
        
        # Explicitly zero the diagonal
        for k in range(b_len):
            dist_sq[k, i + k] = 0.0
            
        np.maximum(dist_sq, 0.0, out=dist_sq)
        np.sqrt(dist_sq, out=dist_sq)
        total += float(dist_sq.sum())
        
    print(f"TOTAL:{total}")

if __name__ == '__main__':
    main()
