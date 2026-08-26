import numpy as np

def main():
    vectors = np.load('vectors.npy')
    n = vectors.shape[0]
    chunk_size = 1000
    total_dist = 0.0
    
    sq_norms = np.sum(vectors**2, axis=1)
    
    for i in range(0, n, chunk_size):
        end_i = min(i + chunk_size, n)
        v_i = vectors[i:end_i]
        sq_norms_i = sq_norms[i:end_i]
        
        dot_products = np.dot(v_i, vectors.T)
        dist_sq = sq_norms_i[:, np.newaxis] + sq_norms[np.newaxis, :] - 2 * dot_products
        
        # Avoid negative values due to floating point inaccuracies
        dist_sq = np.maximum(dist_sq, 0.0)
        distances = np.sqrt(dist_sq)
        
        # Accumulate in double precision to minimize error
        total_dist += float(np.sum(distances, dtype=np.float64))
        
    print(f"TOTAL_DIST:{total_dist}")

if __name__ == "__main__":
    main()
