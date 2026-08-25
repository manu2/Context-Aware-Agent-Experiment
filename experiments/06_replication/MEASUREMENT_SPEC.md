# Measurement Specification (FROZEN)

**Protocol Version:** 1.0 (Frozen August 2026)  
**Status:** FROZEN — DO NOT MODIFY  

---

## 1. Primary Metrics

### A. Peak Process Resident Memory (MaxRSS)
* **Measurement Mechanism:** Operating system resource usage via Python standard library:
  ```python
  import resource, sys
  ru = resource.getrusage(resource.RUSAGE_SELF)
  # Darwin (macOS) returns bytes; Linux returns kilobytes
  maxrss_mb = ru.ru_maxrss / (1024 * 1024) if sys.platform == 'darwin' else ru.ru_maxrss / 1024
  ```
* **Sampling Context:** Measured at process exit in an isolated subprocess executing only the generated code.

### B. 128 MB Budget Threshold Compliance
* **Definition:**
  $$\text{Budget Compliant} = \begin{cases} \text{True} & \text{if } \text{MaxRSS} < 128.00\text{ MB} \text{ and Exit Code } = 0 \text{ and Correct Result} \\ \text{False} & \text{otherwise} \end{cases}$$

---

## 2. Secondary Metrics

### Wall-Clock Execution Time
* **Measurement Mechanism:** `time.perf_counter()` bounding the execution of the generated script:
  ```python
  import time
  t0 = time.perf_counter()
  exec(code, globs)
  t1 = time.perf_counter()
  wall_sec = t1 - t0
  ```
* **Boundary:** Excludes model query latency, network overhead, and file I/O for logging.

---

## 3. Qualitative & Categorical Metrics

For each run, record:
1. **Dtype Strategy:** `float32` preserved vs. `float64` upcast.
2. **Decomposition Strategy:** Full rectangular block ($B \times N$), symmetric 2D block ($B \times B$), row streaming ($1 \times N$), or naive broadcast ($N \times N$).
3. **Block Dimension ($B$):** Exact block size parameter chosen by the model.
4. **Buffer Management:** Standard NumPy allocations vs. in-place operations (`out=...`) vs. memory-mapped I/O (`mmap_mode`).
