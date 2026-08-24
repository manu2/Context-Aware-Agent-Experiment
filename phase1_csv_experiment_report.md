# PHASE 1 EXPERIMENTAL REPORT: SUBSTRATE-AWARE CODE OPTIMIZATION

**Project:** Substrate & Self-Telemetry Conditioned Agentic Computation (SST-SCAC)  
**Experiment Target:** CSV Data Aggregation (2,000,000 rows $\times$ 5 columns, ~85MB raw CSV on disk)  
**Evaluated Model:** `gemini-3.6-flash` (Google Generative AI v1beta REST API)  
**Container Sandbox:** Linux unified `cgroup v2` (`systemd-run --user --scope -p MemoryMax=128M -p MemorySwapMax=0`)  
**Host Environment:** Google Compute Engine `e2-medium` (2 vCPU / 4GB RAM), Ubuntu 24.04 LTS (Kernel 6.8+)  
**Date:** August 23, 2026  

---

## 1. Executive Summary & Objective

The objective of this baseline experiment was to evaluate whether disclosing an explicit hardware RAM constraint (`RAM limit: 128 MB`) in an LLM agent prompt—without providing any prescriptive optimization hints—induces structural algorithmic optimization in the generated code compared to an unconstrained (Blind) baseline.

---

## 2. Experimental Protocol & Prompts

### 2.1 The Interventions
- **Condition A (Blind Baseline)**:
  ```text
  Write a self-contained Python script to process 'data.csv'.
  Group records by 'category_id' and compute the sum of 'metric_val'.
  Print the final total count of unique categories: 'TOTAL_CATEGORIES:<count>'.
  ```
- **Condition B (Substrate-Aware Intervention)**:
  ```text
  Write a self-contained Python script to process 'data.csv'.
  Group records by 'category_id' and compute the sum of 'metric_val'.
  Print the final total count of unique categories: 'TOTAL_CATEGORIES:<count>'.

  Execution environment:
  RAM limit: 128 MB.
  ```

### 2.2 Execution Control
- 9 paired trials were executed sequentially on the target Linux host inside isolated cgroup v2 sandbox scope units.
- Model generation temperature was locked at `0.2`.
- Pre-flight positive control confirmed that allocations exceeding 128MB were deterministically killed by the Linux kernel (`SIGKILL Exit 137`).

---

## 3. Empirical Results & Forensic Code Analysis

### 3.1 Raw Paired Trial Data

| Trial | Condition A (Blind) Code Structure | Condition A Wall Time | Condition B (Substrate-Aware) Code Structure | Condition B Wall Time | Latency Ratio (A / B) | Structural Shift? |
|---|---|---|---|---|---|---|
| **01** | `csv.DictReader` (2M dicts) | 3.07s | `csv.reader` (tuple indexing) | 1.19s | **2.58x faster** | YES |
| **02** | `csv.DictReader` (2M dicts) | 3.74s | `csv.reader` (tuple indexing) | 1.52s | **2.46x faster** | YES |
| **03** | `csv.DictReader` (2M dicts) | 3.03s | `csv.reader` (tuple indexing) | 1.52s | **1.99x faster** | YES |
| **04** | `csv.DictReader` (2M dicts) | 3.06s | `csv.reader` (tuple indexing) | 1.26s | **2.43x faster** | YES |
| **05** | `csv.DictReader` (2M dicts) | 3.01s | `csv.reader` (tuple indexing) | 1.54s | **1.95x faster** | YES |
| **06** | `csv.DictReader` (2M dicts) | 3.05s | `csv.DictReader` (2M dicts) | 3.03s | 1.01x | NO |
| **07** | `csv.DictReader` (2M dicts) | 3.05s | `csv.DictReader` (2M dicts) | 2.99s | 1.02x | NO |
| **08** | `csv.DictReader` (2M dicts) | 3.07s | `csv.reader` (tuple indexing) | 1.50s | **2.05x faster** | YES |
| **09** | `csv.DictReader` (2M dicts) | 3.04s | `csv.DictReader` (2M dicts) | 3.11s | 0.98x | NO |

---

### 3.2 Aggregate Metrics

- **Completion Success Rate**: **100% (9/9)** for both Condition A and Condition B under 128MB RAM.
- **Structural Optimization Shift Rate**: **66.7% (6/9 trials)** shifted from `csv.DictReader` to `csv.reader`.
- **Mean Wall-Clock Execution Time**:
  - Condition A (Blind): **3.12s** ($\sigma = 0.24\text{s}$)
  - Condition B (Substrate-Aware): **1.96s** ($\sigma = 0.81\text{s}$)
  - **Overall Latency Reduction**: **37.2% faster**
- **Diverged Trials Latency Subset (6/9 trials)**:
  - Condition A Mean: **3.16s**
  - Condition B Mean: **1.42s**
  - **Diverged Subset Speedup**: **2.22x faster (55.1% execution time reduction)**

---

## 4. Technical Analysis & Mechanism of Optimization

### 4.1 Why Condition A used `csv.DictReader` (100% of runs)
When unconstrained, `gemini-3.6-flash` consistently chose `csv.DictReader(f)` for readability. In CPython, `DictReader` instantiates a new `dict` object for each of the 2,000,000 rows. This requires 2M dictionary allocations, hash table initializations, and key-value mapping overhead on the Python heap, resulting in execution times between 3.01s and 3.74s.

### 4.2 Why Condition B shifted to `csv.reader` (66.7% of runs)
When injected with `Execution environment: RAM limit: 128 MB`, the model shifted in 6 out of 9 runs to raw `csv.reader(f)` with direct list positional indexing (`row[cat_idx]`). In CPython, `csv.reader` yields lightweight string tuples, bypassing dictionary object allocation overhead and reducing process execution time to 1.19s–1.54s.

### 4.3 Why no OOM Kills (`SIGKILL 137`) occurred
Because the base task prompt did not specify data science libraries, the model defaulted to Python standard library iterators rather than eager Pandas (`pd.read_csv()`). Both `csv.DictReader` and `csv.reader` operate as streaming iterators, keeping peak heap RSS under ~35MB RAM, which fit inside the 128MB container ceiling.

---

## 5. Conclusions & Transition to Phase 2

1. **Substrate Prompting Induces Real Algorithmic Optimization**: Disclosing a RAM limit caused a structural code shift in 66.7% of runs, yielding a 2.22x execution speedup without explicit hints.
2. **Phase 2 Necessity**: To observe actual kernel OOM kills (`SIGKILL 137`) and test true failure recovery, the task must feature algorithms where naive unconstrained implementations naturally allocate memory exceeding the ceiling (e.g. dense matrix products `np.dot(vectors, vectors.T)` allocating 512MB RAM).
