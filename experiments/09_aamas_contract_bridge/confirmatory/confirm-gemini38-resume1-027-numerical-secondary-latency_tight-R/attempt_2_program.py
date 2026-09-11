import numpy as np

# Load the vector array
vectors = np.load("vectors_secondary.npy")

# Convert to float64 for precision and avoid catastrophic cancellation
vectors_64 = vectors.astype(np.float64)
sq_norms = np.sum(vectors_64**2, axis=1)

n = len(vectors_64)
chunk_size = 2000
total = 0.0

# Process in chunks to maintain low memory footprint and high BLAS efficiency
for start in range(0, n, chunk_size):
    end = min(start + chunk_size, n)
    v_chunk = vectors_64[start:end]

    # Compute pairwise squared distances: ||u - v||^2 = ||u||^2 + ||v||^2 - 2*(u . v)
    gram = v_chunk @ vectors_64.T
    d2 = sq_norms[start:end, None] + sq_norms[None, :] - 2.0 * gram

    # Explicitly set diagonal elements to zero
    for idx, row in enumerate(range(start, end)):
        d2[idx, row] = 0.0

    np.maximum(d2, 0.0, out=d2)
    np.sqrt(d2, out=d2)

    total += float(np.sum(d2))

print(f"TOTAL:{total}")
