## Approach

The key challenge is that the full 8,000×8,000 distance matrix would need 256 MB (float32) — way over the 96 MB budget, and the naive double loop over 64M pairs would be far too slow in Python.

**Strategy:**
1. **Gram-matrix identity**: `||a-b||² = ||a||² + ||b||² - 2·a·b`, so one `sgemm` call gives a whole block of squared distances (BLAS does the heavy lifting → ~65 GFLOP total, ~1s).
2. **Row blocking + lower triangle only**: for each row-block `[s,e)` I only multiply against `X[:e]`, halving the FLOPs and capping the scratch buffer at a few MB. Block sums are recombined algebraically (`2·ΣT − ΣW`) to get the full ordered-pair sum.
3. **Memory hygiene**: the scratch buffer is allocated **once** as a flat array and re-`reshape`d, `np.dot(..., out=...)` avoids temporaries, and `np.sum(..., dtype=np.float64)` accumulates in double precision *without* materializing a float64 copy.
4. **Numerical safety**: mean-centering (distances are translation-invariant) minimizes catastrophic cancellation, norms are computed in float64, and negatives are clipped before `sqrt` to avoid NaNs on the diagonal.

```python
#!/usr/bin/env python3
"""Sum of all pairwise Euclidean distances, memory- and time-bounded."""
import numpy as np

FNAME = 'vectors.npy'
BUF_BYTES = 8 << 20          # ~8 MB scratch for the distance block
CHUNK = 1024                 # rows per pass for cheap streaming ops


def main():
    X = np.load(FNAME)
    if X.dtype