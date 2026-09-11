import numpy as np

def main():
    # Load the full array (8000 x 1024 float32 ~ 31 MB, fits comfortably in memory)
    X = np.load('vectors.npy')
    if X.dtype != np.float32:
        X = X.astype(np.float32)

    n = X.shape[0]

    # Precompute squared norms of each row (float64 for better numerical stability)
    norms = np.einsum('ij,ij->i', X, X, dtype=np.float64)

    total = 0.0
    # Process rows in blocks to keep memory usage low.
    # Block size chosen so that block @ X.T stays small (few MB).
    B = 400  # 400 * 8000 * 4 bytes = ~12.8 MB per block matrix

    Xt = X.T  # view, no copy

    for start in range(0, n, B):
        end = min(start + B, n)
        block = X[start:end]                     # (b, 1024) float32
        dot = block.astype(np.float64) @ Xt.astype(np.float64)  # (b, n) float64
        # squared distances
        d2 = norms[start:end][:, None] + norms[None, :] - 2.0 * dot
        np.maximum(d2, 0.0, out=d2)
        np.sqrt(d2, out=d2)
        total += d2.sum(dtype=np.float64)

    # Print result as an exact decimal value
    # Using repr-like formatting to avoid unnecessary truncation
    print(f"TOTAL:{total:.6f}")

if __name__ == "__main__":
    main()
