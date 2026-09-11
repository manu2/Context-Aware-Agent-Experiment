import numpy as np

def main():
    vectors = np.load("vectors.npy")
    
    # Try scipy.spatial.distance.pdist first for minimal memory and maximum accuracy
    try:
        from scipy.spatial.distance import pdist
        dists = pdist(vectors, metric="euclidean")
        total = 2.0 * float(np.sum(dists, dtype=np.float64))
        print(f"TOTAL:{total}")
        return
    except ImportError:
        pass

    # Try PyTorch if scipy is unavailable
    try:
        import torch
        v = torch.from_numpy(vectors)
        total = 0.0
        chunk_size = 500
        for i in range(0, len(v), chunk_size):
            chunk = v[i : i + chunk_size]
            d = torch.cdist(chunk, v, p=2.0)
            total += float(d.sum(dtype=torch.float64).item())
        print(f"TOTAL:{total}")
        return
    except ImportError:
        pass

    # NumPy block-wise fallback to strictly prevent out-of-memory errors
    total = 0.0
    N = len(vectors)
    block_size = 250
    for i in range(0, N, block_size):
        chunk_i = vectors[i : i + block_size]
        for j in range(0, N, block_size):
            chunk_j = vectors[j : j + block_size]
            diff = chunk_i[:, None, :] - chunk_j[None, :, :]
            dists = np.linalg.norm(diff, axis=-1)
            total += float(np.sum(dists, dtype=np.float64))

    print(f"TOTAL:{total}")

if __name__ == "__main__":
    main()
