import numpy as np

def main():
    vectors = np.load('vectors.npy')
    n = vectors.shape[0]
    
    sq_norms = np.sum(vectors ** 2, axis=1)
    
    total = 0.0
    chunk_size = 1000
    
    for i in range(0, n, chunk_size):
        end = min(i + chunk_size, n)
        chunk = vectors[i:end]
        
        # Compute squared Euclidean distance: ||u - v||^2 = ||u||^2 + ||v||^2 - 2<u, v>
        g = chunk @ vectors.T
        dist_sq = sq_norms[i:end, None] + sq_norms[None, :] - 2.0 * g
        
        # Explicitly zero out exact self-distances to avoid precision artifacts
        diag_idx = np.arange(end - i)
        dist_sq[diag_idx, i + diag_idx] = 0.0
        
        np.maximum(dist_sq, 0.0, out=dist_sq)
        np.sqrt(dist_sq, out=dist_sq)
        
        total += np.sum(dist_sq, dtype=np.float64)
        
    print(f"TOTAL:{total}")

if __name__ == '__main__':
    main()
