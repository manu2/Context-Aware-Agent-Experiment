# Exploratory Multi-Model Subagent Pilot Report (Condition A vs Condition D)

**Date:** August 2026  
**Status:** Exploratory Subagent Proxy Pilot (**`paper_draft.md` Strictly Unmodified**)  
**Execution Context:** Exploratory test using isolated Antigravity subagent tiers configured across 3 frontier model proxies to evaluate prompt conditioning behavior.  
**Host Environment:** macOS Darwin (Apple Silicon arm64), Python 3.9.6, NumPy 2.0.2, Single-Threaded BLAS.

---

## 1. Multi-Model Empirical Results Matrix

| Subagent Proxy Label | Condition | Disclosed Limits | Algorithmic Strategy | MaxRSS (MB) | Wall Time (s) | Math Correct? | 128 MB Budget Pass? |
|---|---|---|---|---|---|---|---|
| **GPT-5.6-Sol Proxy** | **Condition A (Blind)** | *None* | Monolithic Gram Matrix (`float64`, unchunked $8000 \times 8000$) | **1,512.67 MB** | **2.212s** | ✅ PASS ($\Delta < 10^{-11}$) | ❌ **FAIL** (Exceeds by 11.8x) |
| **GPT-5.6-Sol Proxy** | **Condition D (2D Tel)** | RAM: 128M, Time: 10s | In-place Row Batching (`batch_size=500`, `float32`) | **119.27 MB** | **0.417s** | ✅ PASS ($\Delta < 10^{-7}$) | ✅ **PASS (12.68x reduction)** |
| **Gemini 3.7 Flash Proxy** | **Condition A (Blind)** | *None* | Row Chunking with `float64` conversion (`batch_size=1000`) | **428.94 MB** | **1.146s** | ✅ PASS ($\Delta < 10^{-15}$) | ❌ **FAIL** (Exceeds by 3.35x) |
| **Gemini 3.7 Flash Proxy** | **Condition D (2D Tel)** | RAM: 128M, Time: 10s | Memory-Mapped In-Place GEMM (`chunk_size=500`, `float32`) | **91.95 MB** | **0.418s** | ✅ PASS ($\Delta < 10^{-10}$) | ✅ **PASS (4.66x reduction)** |
| **Claude Opus 5 Proxy** | **Condition A (Blind)** | *None* | Row Chunking (`chunk_size=1000`, full broadcast dot) | **213.31 MB** | **0.620s** | ✅ PASS ($\Delta < 10^{-7}$) | ❌ **FAIL** (Exceeds by 1.67x) |
| **Claude Opus 5 Proxy** | **Condition D (2D Tel)** | RAM: 128M, Time: 10s | Granular Block Chunking (`block_size=256`, full dot) | **212.19 MB** | **0.559s** | ✅ PASS ($\Delta < 10^{-7}$) | ❌ **FAIL** (Exceeds by 1.66x) |

---

## 2. Exploratory Observations & Cautious Interpretation

These exploratory runs demonstrate the potential effects of substrate telemetry conditioning on generated algorithm selection:

1. **GPT-5.6 Proxy:**
   * In Condition A, allocated an unchunked $8000 \times 8000$ Gram matrix in `float64`, consuming **1,512.67 MB MaxRSS**.
   * In Condition D, shifted to **in-place row batching (`batch_size=500`)**, reducing peak memory to **119.27 MB** and decreasing wall time from **2.212s to 0.417s**.
2. **Gemini 3.7 Proxy:**
   * In Condition A, processed in `float64` batches consuming **428.94 MB MaxRSS**.
   * In Condition D, utilized `mmap_mode="r"` and in-place GEMM (`chunk_size=500`), keeping peak memory at **91.95 MB** with a runtime of **0.418s**.
3. **Claude Opus Proxy:**
   * In Condition A, selected `chunk_size=1000` (peaking at **213.31 MB**).
   * In Condition D, reduced block size to `block_size=256` but retained full un-tiled dot products (`XY = np.dot(X_b, vectors.T)`), keeping peak memory at **212.19 MB**.

---

## 3. Provenance & Artifacts

All prompt inputs, raw subagent completions, generated scripts, and execution metadata have been archived:
* **Claude Opus 5 Proxy:** [Condition A](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/claude-opus-5/opus_pilot_A/) | [Condition D](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/claude-opus-5/opus_pilot_D/)
* **GPT-5.6-Sol Proxy:** [Condition A](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gpt-5.6-sol/gpt_pilot_A/) | [Condition D](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gpt-5.6-sol/gpt_pilot_D/)
* **Gemini 3.7 Flash Proxy:** [Condition A](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gemini-3.7-flash/gemini_pilot_A/) | [Condition D](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gemini-3.7-flash/gemini_pilot_D/)
* **Execution Tracker:** [`experiments/06_replication/PILOT_TRACKER.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/PILOT_TRACKER.md)

**Manuscript Status:** **100% Unmodified**.
