# Execution Environment & System Specification (FROZEN)

**Protocol Version:** 1.0 (Frozen August 2026)  
**Status:** FROZEN — DO NOT MODIFY  

---

## 1. Host Execution System & Environment Fingerprint
* **Operating System:** macOS Darwin (macOS-15.5-arm64-arm-64bit)
* **Kernel Version:** Darwin 24.x (Apple Silicon)
* **Architecture:** `arm64` (Apple Silicon CPU)
* **Python Runtime:** `Python 3.9.6` (standard venv `.venv`)
* **NumPy Version:** `2.0.2`
* **BLAS Backend:** Apple Accelerate BLAS (`vecLib`) / Accelerate Framework
* **Thread Pinning / Determinism:** Enforced single-threaded execution (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`) to eliminate multi-threaded allocator jitter.
* **MaxRSS Unit Semantics:** `resource.getrusage(RUSAGE_SELF).ru_maxrss` in **bytes** on Darwin (converted to MB via `ru_maxrss / (1024 * 1024)`).

---

## 2. Execution Directory & Isolation

* **Working Directory:** Isolated subdirectory with local copy/symlink of `vectors.npy`.
* **Execution Sandbox:** Clean temporary subprocess executing isolated script `python script.py`.
* **Declared Prompt Execution Quota:** 10.0 seconds (disclosed in Condition D prompt and scored post-hoc via `wall_sec <= 10.0s`; not actively enforced by OS kernel during execution).
* **Sandbox Safety Watchdog Ceiling:** 60.0 seconds (hard process termination to prevent infinite loops or hangs).

---

## 3. Immutable Input Data

* **Path:** `data/vectors.npy`
* **SHA-256 Checksum:** `199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085`
