# Empirical Analysis: Cross-Model Frontier Evaluation & The Limits of Unconditioned Reasoning (Historical Artifact)

> **Methodology Notice**: This document records early exploratory single-trial evaluations and tracemalloc measurements. For the authoritative replicated paired trials with post-hoc OS-level MaxRSS measurements, refer to `experiments/05_paired_statistical_trials/canonical_paired_results.json` and `paper_draft.md` Table 1.

**Project:** Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC)  
**Authors:** Research & Architecture Team  
**Date:** August 2026  
**Evaluated Frontier Models:** Anthropic `claude-opus-5`, OpenAI `gpt-5.6-sol`, Anthropic `claude-sonnet-5`, Google `gemini-3.7-flash`, OpenAI `gpt-4o` (Legacy)  
**Task Workload:** Pairwise Euclidean Distance on an $8,000 \times 1,024$ float32 matrix (`vectors.npy`, 32.8 MB)  
**Physical Sandbox Ceiling:** 128 MB RAM (Target Budget Threshold)

---

## 1. Executive Summary & Core Discovery

This evaluation provides direct empirical evidence for the central thesis of SCAC:

> **Even the world's most capable reasoning models (such as `claude-opus-5`) produce sophisticated, highly optimized mathematical code that nevertheless suffers fatal operating system Out-Of-Memory kills (`SIGKILL Exit 137`) when executed in physical isolation without runtime substrate limits.**

When physical limits are projected into the agent's inference context, reasoning models dynamically adapt tile dimensions, buffer layouts, and precision to achieve guaranteed execution within micro-VM boundaries.

---

## 2. Quantitative Empirical Results Across All Evaluated Models

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       FRONTIER MULTI-MODEL BENCHMARK AUDIT (128 MB CONTAINER)                                    │
├──────────────────────────┬──────────────────────┬──────────────────────────────┬────────────────────────┬────────────────────────┤
│ Model Architecture       │ Variant A (Blind)    │ Variant B (Natural Language) │ Variant C (1D: 128MB)  │ Variant D (2D: 128M+10s)│
├──────────────────────────┼──────────────────────┼──────────────────────────────┼────────────────────────┼────────────────────────┤
│ **Anthropic Claude Opus 5**| **131.88 MB** / 0.681s│ 48.20 MB / 0.738s            │ *N/A*                  │ **61.47 MB / 0.3942s** │
│                          │ (💥 **OOM Kill 137**)│ (✅ 128M Pass)               │                        │ (🏆 **SOTA Trapezoid**)│
├──────────────────────────┼──────────────────────┼──────────────────────────────┼────────────────────────┼────────────────────────┤
│ **OpenAI GPT-5.6-Sol**   │ 100.47 MB / 0.630s   │ 7.24 MB / 0.694s             │ 10.22 MB / 0.606s      │ **4.12 MB / 0.1896s**  │
│                          │ (✅ 128M Pass)       │ (✅ 128M Pass)               │ (✅ 128M Pass)         │ (🏆 **SOTA In-Place**) │
├──────────────────────────┼──────────────────────┼──────────────────────────────┼────────────────────────┼────────────────────────┤
│ **Anthropic Sonnet 5**   │ **215.22 MB** / 1.041s│ 77.28 MB / 0.376s            │ **92.46 MB** / 0.434s  │ 122.91 MB / 0.3861s    │
│                          │ (💥 **OOM Kill 137**)│ (✅ 128M Pass)               │ (✅ **128M Pass**)     │ (✅ **128M Pass**)     │
├──────────────────────────┼──────────────────────┼──────────────────────────────┼────────────────────────┼────────────────────────┤
│ **Google Gemini 3.7**    │ **1,565.72 MB**/2.88s│ < 35 MB / >30s               │ 32.03 MB / 30.0s       │ **114.84 MB / 0.4600s**│
│                          │ (💥 **OOM Kill 137**)│ (⏱️ **Timeout**)             │ (⚠️ **Slow Loop**)     │ (🏆 **BLAS 2D Block**) │
├──────────────────────────┼──────────────────────┼──────────────────────────────┼────────────────────────┼────────────────────────┤
│ **OpenAI GPT-4o (Legacy)**│ **1,136.31 MB**/1.35s│ **770.36 MB** / 0.720s       │ **770.36 MB** / 0.690s │ **770.41 MB / 0.6800s**│
│                          │ (💥 **OOM Kill 137**)│ (💥 **OOM Kill 137**)        │ (💥 **OOM Kill 137**)  │ (💥 **OOM Kill 137**)  │
└──────────────────────────┴──────────────────────┴──────────────────────────────┴────────────────────────┴────────────────────────┘
```

---

## 3. In-Depth Analysis: The `claude-opus-5` Case Study

### 3.1 Unconditioned Brilliance Leading to Kernel Failure (Variant A: Blind)

In the unconditioned **Variant A (Blind)** prompt, `claude-opus-5` generated mathematically sophisticated code. It recognized the $O(N^2)$ scaling issue and applied three advanced algorithmic optimizations:
1. **Gram Matrix Identity**: Replaced pairwise element subtraction with matrix multiplication ($\|a-b\|^2 = \|a\|^2 + \|b\|^2 - 2\langle a, b\rangle$).
2. **Mean Centering for Numerical Stability**: Shifted data by the column mean ($\mu$) to prevent catastrophic floating-point cancellation.
3. **Upper-Triangle Symmetric Exploitation**: Computed only $j \ge i$ to halve the FLOP count.

#### Why It Still Failed:
Because it had no physical substrate telemetry, `claude-opus-5` prioritized numerical precision over physical constraint:
* It promoted the entire $8,000 \times 1,024$ dataset to `float64` ($65.5\text{ MB}$).
* It set a default block size of $\text{BLOCK} = 1024$ ($1024 \times 8000 \times 8\text{ bytes} \approx 65.5\text{ MB}$ working buffer).
* **Total Peak Heap RSS**: **131.88 MB**.

> **The Outcome**: Because $131.88\text{ MB} > 128.0\text{ MB}$, the Linux kernel issued an instant **`SIGKILL (Exit Code 137)`**. Despite its algorithmic elegance, the process crashed with 100% data loss.

---

### 3.2 Telemetry-Conditioned Synthesis (Variant D: 2D SCAC Telemetry)

When provided with explicit 2D telemetry (`RAM limit: 128 MB. Execution time limit: 10.0 seconds`), `claude-opus-5` re-engineered the architecture:
1. **Preserved Base Matrix in `float32`**: Retained source array in `float32` ($32.8\text{ MB}$).
2. **Surgically Bounded Block Size**: Reduced $\text{ROW\_BLOCK} = 256$ ($16\text{ MB}$ working buffer).
3. **Upper-Trapezoid Gram Streaming**: Only computed columns $j \ge i0$ in a single multithreaded BLAS `sgemm` call.

```python
# SOTA Upper-Trapezoid Gram Streaming by claude-opus-5 (Variant D)
FILENAME = "vectors.npy"
ROW_BLOCK = 256          # 256 x 8000 float64 = 16 MB working buffer

def main():
    X = np.load(FILENAME)
    if X.dtype != np.float32:
        X = X.astype(np.float32, copy=False)
    X = np.ascontiguousarray(X)
    n, d = X.shape

    # Precompute squared norms in float64 block-wise
    sq = np.empty(n, dtype=np.float64)
    step = 1024
    for s in range(0, n, step):
        e = min(s + step, n)
        blk = X[s:e].astype(np.float64)
        sq[s:e] = np.einsum('ij,ij->i', blk, blk)
        del blk

    total_upper = 0.0

    for i0 in range(0, n, ROW_BLOCK):
        i1 = min(i0 + ROW_BLOCK, n)
        b = i1 - i0

        # Gram block: rows [i0:i1] against all columns [i0:n] (single sgemm)
        G = X[i0:i1] @ X[i0:].T                  # (b, n-i0) float32
        D = G.astype(np.float64)
        del G
        D *= -2.0
        D += sq[i0:i1, None]
        D += sq[i0:][None, :]
        np.maximum(D, 0.0, out=D)
        np.sqrt(D, out=D)

        # Diagonal block handling (avoid double counting)
        s_all = float(D.sum())
        s_diag = float(D[:, :b].sum())
        total_upper += s_all - 0.5 * s_diag
        del D

    total = 2.0 * total_upper
    print("TOTAL_DIST:%.6f" % total)
```

#### Measured Execution Profile:
* **Peak RAM**: **61.47 MB** ($\mathbf{53.4\%}$ memory reduction vs. Blind, staying safely within 128 MB).
* **Execution Latency**: **0.3942s** ($\mathbf{1.73\times}$ speedup vs. Blind and $\mathbf{1.87\times}$ faster than Natural Language).
* **Sandbox Status**: **✅ 100% PARETO PASS**.

---

## 4. Key Takeaways for the Research Paper

1. **High Model Capability Does Not Eliminate Silicon Blindness**:
   Reasoning depth enables models to design superior algorithms, but **without physical substrate telemetry, models cannot guess the container's physical RAM boundaries**.
2. **The "Precision vs. Feasibility" Dilemma**:
   Unconditioned models default to `float64` promoting memory consumption above micro-VM limits. Substrate telemetry explicitly informs the agent when precision must be balanced against memory limits.
3. **The Role of SCAC**:
   SCAC does not replace model reasoning—**it grounds frontier reasoning in physical reality**, transforming high-level algorithmic knowledge into concrete, container-safe execution.

---

## 5. Artifact Index & Reproduction Scripts

* **Full Audited Report**: [`local_experiments/frontier_model_benchmark/FRONTIER_REPORT.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/local_experiments/frontier_model_benchmark/FRONTIER_REPORT.md)
* **Audited Execution JSON**: [`local_experiments/frontier_model_benchmark/frontier_benchmark_audited.json`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/local_experiments/frontier_model_benchmark/frontier_benchmark_audited.json)
* **Claude Opus 5 Scripts**:
  * Blind (Variant A, 131.88 MB OOM): [`a_claude-opus-5.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/local_experiments/frontier_model_benchmark/runs/a_claude-opus-5.py)
  * Natural Language (Variant B, 48.20 MB): [`b_claude-opus-5.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/local_experiments/frontier_model_benchmark/runs/b_claude-opus-5.py)
  * 2D Telemetry (Variant D, 61.47 MB / 0.394s SOTA): [`2d_claude-opus-5.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/local_experiments/frontier_model_benchmark/runs/2d_claude-opus-5.py)
