import numpy as np

def main():
    # Memory-map vectors to keep RSS minimal
    X = np.load('vectors.npy', mmap_mode='r')
    N = X.shape[0]
    
    # Precompute squared L2 norms for all vectors (shape: (N,))
    # Accumulate row-wise squares in float32
    sq_norms = np.einsum('ij,ij->i', X, X)
    
    block_size = 1000
    off_diag_sum = 0.0
    
    # Loop over upper-triangular blocks
    for r_start in range(0, N, block_size):
        r_end = min(r_start + block_size, N)
        X_r = X[r_start:r_end]
        sq_norms_r = sq_norms[r_start:r_end, None]
        
        for c_start in range(r_start, N, block_size):
            c_end = min(c_start + block_size, N)
            X_c = X[c_start:c_end]
            sq_norms_c = sq_norms[None, c_start:c_end]
            
            # Compute dot products between blocks: (r_len, c_len)
            D = X_r @ X_c.T
            
            # D = ||u||^2 + ||v||^2 - 2<u, v>
            D *= -2.0
            D += sq_norms_r
            D += sq_norms_c
            
            # Clamp negative values due to floating-point roundoff
            np.maximum(D, 0.0, out=D)
            np.sqrt(D, out=D)
            
            if r_start == c_start:
                # Same block: extract strictly upper-triangular part
                i_idx, j_idx = np.triu_indices(r_end - r_start, k=1)
                off_diag_sum += float(np.sum(D[i_idx, j_idx], dtype=np.float64))
            else:
                # Off-diagonal block: all pairs are strictly i < j
                off_diag_sum += float(np.sum(D, dtype=np.float64))
                
    # All ordered pairs sum = 2 * sum_{i < j} d(v_i, v_j)
    total = 2.0 * off_diag_sum
    print(f"TOTAL:{total}")

if __name__ == '__main__':
    main()
