# Condition A / Condition D Parity Audit

**Date:** August 2026  
**Artifact Scope:** Controlled comparison of Condition A (Blind) vs. Condition D (Substrate-Aware).  

---

## 1. Structured Condition Comparison Matrix

| Dimension | Condition A (Blind) | Condition D (Substrate-Aware) | Status / Parity Check |
|---|---|---|---|
| **Base Computational Task** | Compute pairwise Euclidean sum of `vectors.npy` ($8000 \times 1024$ float32) | Compute pairwise Euclidean sum of `vectors.npy` ($8000 \times 1024$ float32) | ✅ **100% Identical** |
| **Output Requirement** | Print `TOTAL_DIST:<value>` | Print `TOTAL_DIST:<value>` | ✅ **100% Identical** |
| **Library Constraints** | NumPy + Python standard library only | NumPy + Python standard library only | ✅ **100% Identical** |
| **Input File & Hash** | `vectors.npy` (SHA-256: `199a60e06...`) | `vectors.npy` (SHA-256: `199a60e06...`) | ✅ **100% Identical** |
| **RAM Resource Information** | *None* | `RAM limit: 128 MB.` | 🔬 **Intended Experimental Variable** |
| **Time Resource Information** | *None* | `Execution time limit: 10.0 seconds.` | 🔬 **Intended Experimental Variable** |
| **Algorithm & Optimization Hints** | *None* | *None* (No mention of chunking, block size, streaming, symmetry, in-place ops, or dtype conversion) | ✅ **100% Clean (Zero Optimization Leaks)** |
| **Implementation Hints** | *None* | *None* | ✅ **100% Clean** |
| **System Instructions** | *None* (Empty system prompt across both) | *None* (Empty system prompt across both) | ✅ **100% Identical** |
| **Sampling Controls** | Provider-compatible controls: Claude Opus 5 provider defaults (its API rejects explicit sampling); Gemini $T=0.1$; OpenAI $T=1.0$ | Identical provider-compatible controls within each paired run | ✅ **100% Matched** |
| **Execution Environment** | Isolated subprocess on macOS Darwin arm64 (Python 3.9.6, NumPy 2.0.2) | Isolated subprocess on macOS Darwin arm64 (Python 3.9.6, NumPy 2.0.2) | ✅ **100% Matched** |

---

## 2. Verbatim Prompt Texts

### Condition A (Blind Baseline):
```text
Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages.
```

### Condition D (Substrate-Aware):
```text
Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages.

Execution environment:
RAM limit: 128 MB.
Execution time limit: 10.0 seconds.
```

---

## 3. Accidental Difference Audit & Verification

* **Did Condition D contain any algorithmic hints in the paired trials?**
  * **No.** Earlier prompt tests in `multi_model_benchmark.py` (an exploratory script) had an exploratory variant with strategy suggestions (`Optimization Strategy: Use vectorized block/chunk processing`), but the actual replicated paired trials (`run_paired_trials.py`, line 162) used the clean constraint-only prompt shown above.
* **Are there differences in tool access or few-shot examples?**
  * **No.** Both conditions are evaluated under strictly zero-shot prompt completion. Zero few-shot examples, zero tool definitions, and zero interactive feedback loops were provided.
* **Parity Verdict:** The difference between Condition A and Condition D consists **solely of the two-line execution environment constraint specification**.
