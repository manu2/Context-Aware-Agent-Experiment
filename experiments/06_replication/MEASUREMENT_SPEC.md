# Measurement Specification (FROZEN)

**Protocol Version:** 1.0 (Frozen August 2026)  
**Status:** FROZEN — DO NOT MODIFY  

---

## 1. Primary Metrics

### A. Peak Process Resident Memory (MaxRSS)
* **Measurement Mechanism:** Operating system resource usage via Python standard library:
  ```python
  import resource, sys
  # Called in the profiler wrapper after its one generated-script child exits.
  ru = resource.getrusage(resource.RUSAGE_CHILDREN)
  # Darwin (macOS) returns bytes; Linux returns kilobytes
  maxrss_mb = ru.ru_maxrss / (1024 * 1024) if sys.platform == 'darwin' else ru.ru_maxrss / 1024
  ```
* **Sampling Context:** A short-lived profiler wrapper launches exactly one isolated generated-script child (`python script.py`) and reads `RUSAGE_CHILDREN` after that child exits. This reports the child process's peak resident memory rather than the runner's own heap.

### B. 128 MB Budget Threshold Compliance
* **Definition:**
  $$\text{Budget Compliant} = \begin{cases} \text{True} & \text{if } \text{MaxRSS} < 128.00\text{ MB} \text{ and Exit Code } = 0 \text{ and Correct Result} \\ \text{False} & \text{otherwise} \end{cases}$$

---

## 2. Secondary Metrics

### Wall-Clock Execution Time
* **Measurement Mechanism:** Total execution duration of the isolated process measured from the runner parent via `time.perf_counter()` or internal script execution block:
  ```python
  import time
  t0 = time.perf_counter()
  proc = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
  t1 = time.perf_counter()
  wall_sec = t1 - t0
  ```
* **Boundary:** Excludes model generation latency, API network calls, and report formatting.

---

## 3. Qualitative & Categorical Metrics

For each run, record:
1. **Dtype Strategy:** `float32` preserved vs. `float64` upcast.
2. **Decomposition Strategy:** Full rectangular block ($B \times N$), symmetric 2D block ($B \times B$), row streaming ($1 \times N$), or naive broadcast ($N \times N$).
3. **Block Dimension ($B$):** Exact block size parameter chosen by the model.
4. **Buffer Management:** Standard NumPy allocations vs. in-place operations (`out=...`) vs. memory-mapped I/O (`mmap_mode`).
