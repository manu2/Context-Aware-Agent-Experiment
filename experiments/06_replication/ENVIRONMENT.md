# Execution Environment & System Specification (FROZEN)

**Protocol Version:** 1.0 (Frozen August 2026)  
**Status:** FROZEN — DO NOT MODIFY  

---

## 1. Host Execution System

* **Operating System:** macOS Darwin (arm64, Apple Silicon)
* **Kernel Version:** Darwin 24.x
* **Python Runtime:** Python 3.9.6 / 3.10+ (standard venv `.venv`)
* **NumPy Version:** 1.24+ / 2.x
* **BLAS Backend:** Apple Accelerate BLAS (`vecLib`) / OpenBLAS
* **MaxRSS Unit Semantics:** `resource.getrusage(RUSAGE_SELF).ru_maxrss` in **bytes** (converted to MB via `ru_maxrss / (1024 * 1024)`).

---

## 2. Execution Directory & Isolation

* **Working Directory:** Isolated subdirectory with local copy/symlink of `vectors.npy`.
* **Execution Sandbox:** Clean temporary subprocess executing `python -c "exec(code)"`.
* **Timeout Limit:** 60.0 seconds per script run.

---

## 3. Immutable Input Data

* **Path:** `data/vectors.npy`
* **SHA-256 Checksum:** `199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085`
