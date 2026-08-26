# Replication Conditions Specification (FROZEN)

**Protocol Version:** 1.0 (Frozen August 2026)  
**Status:** FROZEN — DO NOT MODIFY  

---

## 1. Condition A: Blind Baseline (Unconstrained)

### Exact Prompt:
```text
Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages.
```

---

## 2. Condition D: Substrate-Aware (2D Telemetry)

### Exact Prompt:
```text
Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages.

Execution environment:
RAM limit: 128 MB.
Execution time limit: 10.0 seconds.
```

---

## 3. Strict Parity Guarantee
* **Zero Optimization Guidance**: Neither prompt contains optimization advice or algorithmic hints such as blocking, tiling, chunking, streaming, symmetry exploitation, in-place buffer operations, or data type conversion. (Both prompts specify processing the standard float32 `vectors.npy` dataset without specifying how to structure the computation).
* **Single Experimental Factor**: The only difference between Condition A and Condition D is the two-line declaration of the execution environment limits (`RAM limit: 128 MB.`, `Execution time limit: 10.0 seconds.`).
