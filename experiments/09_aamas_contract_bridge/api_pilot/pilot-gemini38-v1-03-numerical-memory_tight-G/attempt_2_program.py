import numpy as np

def main():
    # Load vectors in read-only mode to prevent any modification
    X = np.load('vectors.npy', mmap_mode='r')
    
    # Cast to float64 for numerical precision
    X_64 = X.astype(np.float64)
    sq_norms = np.sum(X_64 ** 2, axis=1)
    
    N = len(X_64)
    chunk_size = 1000
    total_distance = 0.0
    
    for i in range(0, N, chunk_size):
        chunk = X_64[i:i + chunk_size]
        
        # ||u - v||^2 = ||u||^2 + ||v||^2 - 2 <u, v>
        # Shape: (len(chunk), N)
        dists_sq = sq_norms[i:i + len(chunk), None] + sq_norms[None, :] - 2.0 * (chunk @ X_64.T)
        
        # Explicitly set diagonal to zero
        row_idx = np.arange(len(chunk))
        col_idx = i + row_idx
        dists_sq[row_idx, col_idx] = 0.0
        
        # Clamp negative values caused by floating-point inaccuracies
        np.maximum(dists_sq, 0.0, out=dists_sq)
        
        total_distance += float(np.sqrt(dists_sq, out=dists_sq).sum())
        
    print(f"TOTAL:{total_distance}")

if __name__ == '__main__':
    main()
