# Task Audit: Out-of-Core Pairwise Euclidean Distance Benchmark

**Date:** August 2026  
**Artifact Scope:** Audit of task definition across historical paired trials and replication setup.  

---

## 1. Exact Benchmark Task Wording

The exact base prompt provided to models across the historical paired trials (`experiments/05_paired_statistical_trials/run_paired_trials.py`, lines 155–158) and the replication suite is:

```text
Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages.
```

---

## 2. Input Dimensions & Data Characteristics

* **Matrix Dimensions:** $N = 8,000$ rows, $D = 1,024$ columns.
* **Data Type:** Single-precision IEEE 754 32-bit floating point (`numpy.float32`).
* **On-Disk File Format:** NumPy binary array (`vectors.npy`, version 1.0/2.0 header).
* **Raw Array Memory Size:**
  $$\text{Array Size} = 8,000 \times 1,024 \times 4\text{ bytes} = 32,768,000\text{ bytes} = 32.768\text{ MB} \approx 31.25\text{ MiB}$$
* **Mathematical Operations Required:**
  $$\text{Total Dist} = \sum_{i=0}^{N-1} \sum_{j=0}^{N-1} \|v_i - v_j\|_2$$
  * Total pairwise terms: $N \times N = 64,000,000$ evaluations.
  * Symmetric property: $\|v_i - v_j\|_2 = \|v_j - v_i\|_2$, with diagonal terms $\|v_i - v_i\|_2 = 0.0$.
  * Strictly upper-triangular terms: $\frac{N(N-1)}{2} = \frac{8000 \times 7999}{2} = 31,996,000$ pairs.

---

## 3. Required Output & Format

* **Standard Output Format:** Exactly `TOTAL_DIST:<value>` printed to `stdout` (e.g. `TOTAL_DIST:2895556144.199324`).
* **Logging/Diagnostics:** Models may print informational logs or progress indicators to `stderr`.

---

## 4. Expected Correctness Criterion

* **Ground Truth Total Distance:** $\approx 2,895,556,144.20 \pm 100.0$ (variations depending on floating-point summation order and precision).
* **Relative Error Tolerance:**
  $$\text{Relative Error} = \frac{|\text{Computed} - \text{Reference}|}{\text{Reference}} < 10^{-4}$$
* **Exit Code:** Return code `0` (`sys.exit(0)` or normal script termination).

---

## 5. Resource Characteristics Relevant to the Experiment

* **Eager Naive Allocation (Failure Mode):**
  * Materializing the full $8,000 \times 8,000$ pairwise distance matrix in `float64`:
    $$8,000 \times 8,000 \times 8\text{ bytes} = 512,000,000\text{ bytes} = 512\text{ MB}$$
  * Materializing in `float32`:
    $$8,000 \times 8,000 \times 4\text{ bytes} = 256,000,000\text{ bytes} = 256\text{ MB}$$
  * Promoting input to `float64`:
    $$8,000 \times 1,024 \times 8\text{ bytes} = 65.536\text{ MB}$$
* **Target Budget Threshold:** **128 MB RAM** ceiling.
* **Streaming/Tiling Memory Footprint (Success Mode):**
  * Block size $B = 2,000 \times 2,000$ in `float32`:
    $$2,000 \times 2,000 \times 4\text{ bytes} = 16.0\text{ MB}$$
  * Total process RSS with NumPy overhead: $\approx 78\text{ MB} - 105\text{ MB}$ (strictly $< 128\text{ MB}$).

---

## 6. Immutable Input Artifact & Hash

* **File Location:** `data/vectors.npy`
* **File Size:** $32,768,128\text{ bytes}$
* **SHA-256 Checksum:**
  ```
  199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085
  ```
* **Generation Recipe:** Deterministic Gaussian distribution:
  ```python
  np.random.seed(42)
  mat = np.random.randn(8000, 1024).astype(np.float32)
  np.save("vectors.npy", mat)
  ```

---

## 7. Task Parity Determination: Condition A vs. Condition D

* **Do Condition A and Condition D receive the exact same computational task?**
  * **YES.** Both conditions specify the exact same input file (`vectors.npy`), same dimensions ($8000 \times 1024$), same float32 type, same mathematical formula ($\sum_{i,j} \|v_i - v_j\|_2$), same output format (`TOTAL_DIST:<value>`), and same library constraint (NumPy + standard library only).
  * The **only** difference is the appended execution constraint block in Condition D.
