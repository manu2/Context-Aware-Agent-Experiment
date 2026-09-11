An efficient implementation in Python to compute the sum of Euclidean distances over all ordered pairs of rows.

The program uses 64-bit precision matrix multiplication (BLAS Level 3 GEMM) to compute pairwise squared Euclidean distances accurately and efficiently while keeping memory footprint minimal through in-place operations.

```python
import numpy as np


def main():
    # Load vectors (8000, 1024)
    vectors = np.load("vectors.npy")

    # Cast to float64 to avoid numerical instability and catastrophic cancellation
    X = vectors.astype(np.float64)
    del vectors

    # Precompute squared L2 norms for each row: shape (8000, 1)
    sq_norms
