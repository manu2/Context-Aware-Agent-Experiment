import numpy as np

vectors = np.load("vectors.npy")
n = len(vectors)

total = 0.0
for i in range(n - 1):
    diff = vectors[i + 1 :] - vectors[i]
    dist = np.sqrt(np.sum(diff * diff, axis=1, dtype=np.float64))
    total += dist.sum()

total *= 2.0
print(f"TOTAL:{total}")
