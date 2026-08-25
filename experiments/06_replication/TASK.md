# Replication Task Specification (FROZEN)

**Protocol Version:** 1.0 (Frozen August 2026)  
**Status:** FROZEN — DO NOT MODIFY  

---

## 1. Exact Base Task Prompt

The following text is the exact, unparaphrased base prompt to be provided to all models:

```text
Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages.
```

---

## 2. Input Dataset Specification

* **Filename:** `vectors.npy`
* **Array Shape:** `(8000, 1024)`
* **Data Type:** `numpy.float32`
* **File Size:** `32,768,128 bytes`
* **SHA-256 Checksum:**
  ```
  199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085
  ```

---

## 3. Correctness & Output Requirements

* **Required Output:** Script must print `TOTAL_DIST:<value>` to standard output.
* **Ground Truth Value:** $\approx 2895556144.20$
* **Validation Tolerance:** Relative error $< 10^{-4}$ ($0.01\%$).
* **Exit Code:** `0`
