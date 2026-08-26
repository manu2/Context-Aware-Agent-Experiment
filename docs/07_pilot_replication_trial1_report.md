# Pilot Replication Trial 1 Report (Condition A vs Condition D)

**Date:** August 2026  
**Status:** Verification Run (Manuscript Unmodified)  
**Execution Environment:** macOS Darwin (Apple Silicon arm64), Python 3.9.6, NumPy 2.0.2, Single-Threaded BLAS.

---

## 1. Overview & Setup

We conducted a live end-to-end paired trial across **Condition A (Blind)** and **Condition D (2D Substrate Telemetry)** under the frozen replication harness to verify the complete synthesis, execution, profiling, and mathematical validation pipeline.

| Metric / Parameter | Condition A (Blind) | Condition D (2D Telemetry) | Delta / Factor |
|---|---|---|---|
| **Prompt Disclosed RAM Limit** | *None* | `RAM limit: 128 MB` | — |
| **Prompt Disclosed Time Limit** | *None* | `Execution time limit: 10.0 seconds` | — |
| **Synthesized Algorithm** | Monolithic Gram Matrix (`V @ V.T` in `float64`) | Upper-Triangular Block Matrix (`block_size=1000`, `float32` + `2x` symmetry) | **Algorithmic Transition** |
| **Peak Memory (MaxRSS)** | **1,056.16 MB** | **119.83 MB** | **8.81x reduction (-88.65%)** |
| **Execution Time** | **1.767s** | **0.346s** | **5.11x speedup** |
| **Calculated Distance** | `2895556144.199336` | `2895556139.557976` | Relative Error: $1.6 \times 10^{-9}$ |
| **Mathematical Correctness** | ✅ PASS ($< 10^{-4}$) | ✅ PASS ($< 10^{-4}$) | Both mathematically verified |
| **128 MB Budget Compliance** | ❌ **FAIL** (Exceeds by 8.25x) | ✅ **PASS** (< 128.00 MB) | **0/1 vs 1/1** |
| **10.0s Time Budget Compliance** | ✅ PASS | ✅ PASS | Both within limit |

---

## 2. Key Findings & Behavioral Observations

1. **Silicon Blindness Confirmed in Condition A:**
   * In Condition A (Blind), the model cast the entire $8,000 \times 1,024$ matrix to `float64` ($65.5\text{ MB}$) and allocated an unchunked full $8,000 \times 8,000$ `float64` Gram matrix ($512.0\text{ MB}$) alongside intermediate Euclidean distance matrices, peaking at **1,056.16 MB MaxRSS**.
2. **Substrate Awareness in Condition D:**
   * In Condition D (128 MB RAM, 10.0s budget), the model selected an upper-triangular block-tiled matrix multiplication (`block_size=1000`) and exploited symmetric distance properties (`full_sum = 2.0 * total_dist`).
   * This kept peak MaxRSS at **119.83 MB**, cleanly fitting beneath the **128.00 MB ceiling**.
   * Execution time dropped from **1.767s to 0.346s (5.11x speedup)** due to halved FLOP count ($N(N-1)/2$ instead of full $N^2$).

---

## 3. Provenance & Artifacts

* **Raw Condition A Script:** [`experiments/06_replication/raw/gemini-2.0-flash/gemini_rep01_A/script.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gemini-2.0-flash/gemini_rep01_A/script.py)
* **Raw Condition D Script:** [`experiments/06_replication/raw/gemini-2.0-flash/gemini_rep01_D/script.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gemini-2.0-flash/gemini_rep01_D/script.py)
* **Manuscript Status:** **Unmodified** (Awaiting discussion and peer review consensus).
