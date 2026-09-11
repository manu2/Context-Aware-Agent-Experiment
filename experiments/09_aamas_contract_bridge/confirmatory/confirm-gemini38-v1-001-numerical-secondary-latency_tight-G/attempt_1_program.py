import numpy as np

def main():
    # Load input array (8000 x 1024, float32)
    X = np.load('vectors_secondary.npy')
    
    # Cast to float64 to ensure high precision and prevent catastrophic cancellation
    X64 = X.astype(np.float64)
    
    # Compute squared norms for each vector
    sq_norms = np.sum(X64 ** 2, axis=1)
    
    # Compute pairwise squared Euclidean distances: ||u - v||^2 = ||u||^2 + ||v||^2 - 2 * (u . v)
    # Using BLAS level-3 matrix multiplication
    D2 = X64 @ X64.T
    D2 *= -2.0
    D2 += sq_norms[:, None]
    D2 += sq_norms[None, :]
    
    # Numerical guard: clamp values below zero and explicitly zero the diagonal
    np.maximum(D2, 0.0, out=D2)
    np.fill_diagonal(D2, 0.0)
    
    # Compute Euclidean distances in-place
    np.sqrt(D2, out=D2)
    
    # Compute total sum over all ordered pairs
    total = D2.sum()
    
    print(f"TOTAL:{total}")

if __name__ == '__main__':
    main()
