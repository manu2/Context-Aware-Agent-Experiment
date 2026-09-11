import os
import math

def available_cpus():
    try:
        count = len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        count = os.cpu_count() or 1

    try:
        with open("/sys/fs/cgroup/cpu.max", "r", encoding="ascii") as f:
            quota, period = f.read().split()
        if quota != "max":
            count = min(count, max(1, math.ceil(int(quota) / int(period))))
    except (OSError, ValueError, ZeroDivisionError):
        try:
            with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us", "r", encoding="ascii") as f:
                quota = int(f.read())
            with open("/sys/fs/cgroup/cpu/cpu.cfs_period_us", "r", encoding="ascii") as f:
                period = int(f.read())
            if quota > 0 and period > 0:
                count = min(count, max(1, math.ceil(quota / period)))
        except (OSError, ValueError):
            pass

    return max(1, min(count, 32))

_threads = str(available_cpus())
os.environ["OPENBLAS_NUM_THREADS"] = _threads
os.environ["OMP_NUM_THREADS"] = _threads
os.environ["MKL_NUM_THREADS"] = _threads
os.environ["BLIS_NUM_THREADS"] = _threads
os.environ["VECLIB_MAXIMUM_THREADS"] = _threads

import numpy as np

x = np.load("vectors_secondary.npy", allow_pickle=False)
norms = np.einsum("ij,ij->i", x, x, dtype=np.float32)

n = x.shape[0]
block_size = 256
total = 0.0

for start in range(0, n, block_size):
    stop = min(start + block_size, n)
    rows = stop - start

    distances = x[start:stop] @ x[start:].T
    distances *= np.float32(-2.0)
    distances += norms[start:stop, None]
    distances += norms[None, start:]
    np.maximum(distances, np.float32(0.0), out=distances)
    np.sqrt(distances, out=distances)

    diagonal_indices = np.arange(rows)
    distances[diagonal_indices, diagonal_indices] = np.float32(0.0)

    total += float(np.sum(distances[:, :rows], dtype=np.float64))
    if stop < n:
        total += 2.0 * float(np.sum(distances[:, rows:], dtype=np.float64))

print(f"TOTAL:{total}")
