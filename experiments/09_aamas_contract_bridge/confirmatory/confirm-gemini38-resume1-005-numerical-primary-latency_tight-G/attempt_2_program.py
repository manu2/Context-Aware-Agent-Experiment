import numpy as np

def main():
    # Load input array
    vectors = np.load('vectors.npy')
    
    # Convert to float64 for numerical precision
    X = vectors.astype(np.float64)
    
    # Center vectors to maximize numerical stability (Euclidean distance is translation-invariant)
    X -= np.mean(X, axis=0, keepdims=True)
    
    # Squared norms of each row
    sq = np.sum(X ** 2, axis=1)
    
    # Compute Gram matrix using optimized multi-threaded BLAS
    G = X @ X.T
    
    # Compute squared Euclidean distances in-place: sq_i + sq_j - 2 * (x_i . x_j)
    G *= -2.0
    G += sq[:, None]
    G += sq[None, :]
    
    # Ensure exact zero on the diagonal and clip any numerical underflow below zero
    np.fill_diagonal(G, 0.0)
    np.maximum(G, 0.0, out=G)
    np.sqrt(G, out=G)
    
    total = float(np.sum(G))
    print(f"TOTAL:{total}")

if __name__ == '__main__':
    main()
