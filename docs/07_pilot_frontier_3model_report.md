# Pilot Frontier 3-Model Replication Report (Condition A vs Condition D)

**Date:** August 2026  
**Status:** Verification Run (**`paper_draft.md` Strictly Unmodified**)  
**Models Evaluated:**
1. `claude-opus-5`
2. `gpt-5.6-sol`
3. `gemini-3.7-flash`

**Host Environment:** macOS Darwin (Apple Silicon arm64), Python 3.9.6, NumPy 2.0.2, Single-Threaded BLAS.

---

## 1. Multi-Model Empirical Results Matrix

| Frontier Model | Condition | Disclosed Limits | Algorithmic Strategy | MaxRSS (MB) | Wall Time (s) | Math Correct? | 128 MB Budget Pass? |
|---|---|---|---|---|---|---|---|
| **GPT-5.6-Sol** | **Condition A (Blind)** | *None* | Monolithic Gram Matrix (`float64`, unchunked $8000 \times 8000$) | **1,512.67 MB** | **2.212s** | ✅ PASS ($\Delta < 10^{-11}$) | ❌ **FAIL** (Exceeds by 11.8x) |
| **GPT-5.6-Sol** | **Condition D (2D Tel)** | RAM: 128M, Time: 10s | In-place Row Batching (`batch_size=500`, `float32`) | **119.27 MB** | **0.417s** | ✅ PASS ($\Delta < 10^{-7}$) | ✅ **PASS (12.68x reduction)** |
| **Gemini 3.7 Flash** | **Condition A (Blind)** | *None* | Row Chunking with `float64` conversion (`batch_size=1000`) | **428.94 MB** | **1.146s** | ✅ PASS ($\Delta < 10^{-15}$) | ❌ **FAIL** (Exceeds by 3.35x) |
| **Gemini 3.7 Flash** | **Condition D (2D Tel)** | RAM: 128M, Time: 10s | Memory-Mapped In-Place GEMM (`chunk_size=500`, `float32`) | **91.95 MB** | **0.418s** | ✅ PASS ($\Delta < 10^{-10}$) | ✅ **PASS (4.66x reduction)** |
| **Claude Opus 5** | **Condition A (Blind)** | *None* | Row Chunking (`chunk_size=1000`, full broadcast dot) | **213.31 MB** | **0.620s** | ✅ PASS ($\Delta < 10^{-7}$) | ❌ **FAIL** (Exceeds by 1.67x) |
| **Claude Opus 5** | **Condition D (2D Tel)** | RAM: 128M, Time: 10s | Granular Block Chunking (`block_size=256`, full dot) | **212.19 MB** | **0.559s** | ✅ PASS ($\Delta < 10^{-7}$) | ❌ **FAIL** (Exceeds by 1.66x) |

---

## 2. Key Scientific Observations

### 1. GPT-5.6-Sol: Definitive Silicon Awareness Shift
* **Blind Mode (Condition A):** Eagerly cast the dataset to `float64` and performed an unchunked matrix dot-product `G = np.dot(X, X.T)` creating a 512 MB Gram matrix plus 512 MB distance matrix plus float64 arrays, peaking at **1,512.67 MB RAM**.
* **Substrate-Aware Mode (Condition D):** Switched to **in-place row batching (`batch_size=500`)**, reducing peak memory to **119.27 MB** (a **12.68x memory reduction**) and accelerating runtime from **2.212s to 0.417s (5.30x speedup)**.

### 2. Gemini 3.7 Flash: Memory-Mapped Substrate Optimization
* **Blind Mode (Condition A):** Used `float64` chunks, consuming **428.94 MB MaxRSS**.
* **Substrate-Aware Mode (Condition D):** Utilized `mmap_mode="r"` memory mapping and in-place GEMM (`chunk_size=500`), keeping peak memory to **91.95 MB** (a **4.66x memory reduction**) with a **2.74x speedup** ($1.146\text{s} \rightarrow 0.418\text{s}$).

### 3. Claude Opus 5: Block Size Reduction & Baseline Memory Ceiling
* **Blind Mode (Condition A):** Selected `chunk_size=1000` but computed `np.dot(v_i, vectors.T)`, peaking at **213.31 MB**.
* **Substrate-Aware Mode (Condition D):** Reduced block size to `block_size=256`, but still retained full matrix dot multiplication in memory (`XY = np.dot(X_b, vectors.T)`), peaking at **212.19 MB**. (This mirrors the exact empirical phenomenon documented in the Phase 2 audit where un-tiled dot products hover between $196–238\text{ MB}$).

---

## 3. Provenance & Reproducibility Links

All generated trial scripts have been archived with zero post-hoc modifications:
* **Claude Opus 5:**
  * [Condition A (Blind)](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/claude-opus-5/opus_pilot_A/script.py)
  * [Condition D (2D Telemetry)](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/claude-opus-5/opus_pilot_D/script.py)
* **GPT-5.6-Sol:**
  * [Condition A (Blind)](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gpt-5.6-sol/gpt_pilot_A/script.py)
  * [Condition D (2D Telemetry)](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gpt-5.6-sol/gpt_pilot_D/script.py)
* **Gemini 3.7 Flash:**
  * [Condition A (Blind)](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gemini-3.7-flash/gemini_pilot_A/script.py)
  * [Condition D (2D Telemetry)](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/06_replication/raw/gemini-3.7-flash/gemini_pilot_D/script.py)

**Manuscript Status:** **100% Unmodified**.
