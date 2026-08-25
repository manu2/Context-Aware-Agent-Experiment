# Algorithmic Classification Audit: 20 Historical Canonical Trial Scripts

**Date:** August 2026  
**Artifact Scope:** Ground-truth static code inspection of all 20 archived scripts in `experiments/05_paired_statistical_trials/runs/`.  

---

## 1. Classification Matrix Across All 20 Archived Scripts

| Model | Condition | Trial | Algorithmic Strategy | Input Dtype | Materialized Intermediate Structures | MaxRSS (MB) | 128M Budget Result |
|---|---|---|---|---|---|---|---|
| **Claude Opus 5** | **A (Blind)** | **T1** | Row-blocked Gram ($B=512$), non-symmetric product ($B \times N$) | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ ($G$) + selfcheck | **205.69** | 💥 Exceeds (>128M) |
| **Claude Opus 5** | **D (Aware)** | **T1** | Symmetric 2D block tiling ($B=2000$), upper-triangle only | `float32` ($32.8\text{ MB}$) | $2000 \times 2000 \times 4\text{ B} = 16.0\text{ MB}$ ($C$, deleted in loop) | **82.48** | ✅ Within Budget |
| **Claude Opus 5** | **A (Blind)** | **T2** | Mean-centered row-blocked Gram ($B=512$), upper cols ($j \ge i$) | `float64` ($65.5\text{ MB}$) | Up to $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ | **162.95** | 💥 Exceeds (>128M) |
| **Claude Opus 5** | **D (Aware)** | **T2** | Symmetric 2D block tiling ($B=2000$), upper-triangle only | `float32` ($32.8\text{ MB}$) | $2000 \times 2000 \times 4\text{ B} = 16.0\text{ MB}$ (reused in loop) | **99.17** | ✅ Within Budget |
| **Claude Opus 5** | **A (Blind)** | **T3** | Mean-centered blocked Gram ($B=512$), non-symmetric product ($B \times N$) | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ + norm broadcasts | **239.75** | 💥 Exceeds (>128M) |
| **Claude Opus 5** | **D (Aware)** | **T3** | Symmetric 2D block tiling ($B=2000$), upper-triangle only | `float32` ($32.8\text{ MB}$) | $2000 \times 2000 \times 4\text{ B} = 16.0\text{ MB}$ | **104.38** | ✅ Within Budget |
| **Claude Opus 5** | **A (Blind)** | **T4** | Blocked Gram ($B=512$), full rectangular evaluation ($B \times N$) | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ + square root matrix | **291.78** | 💥 Exceeds (>128M) |
| **Claude Opus 5** | **D (Aware)** | **T4** | Symmetric 2D block tiling ($B=2000$), upper-triangle only | `float32` ($32.8\text{ MB}$) | $2000 \times 2000 \times 4\text{ B} = 16.0\text{ MB}$ | **91.34** | ✅ Within Budget |
| **Claude Opus 5** | **A (Blind)** | **T5** | Blocked Gram ($B=512$), full rectangular evaluation ($B \times N$) | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ + temporary buffers | **291.83** | 💥 Exceeds (>128M) |
| **Claude Opus 5** | **D (Aware)** | **T5** | Symmetric 2D block tiling ($B=2000$), upper-triangle only | `float32` ($32.8\text{ MB}$) | $2000 \times 2000 \times 4\text{ B} = 16.0\text{ MB}$ | **90.47** | ✅ Within Budget |
| **GPT-5.6-Sol** | **A (Blind)** | **T1** | Row-blocked Gram ($B=512$), float64 promotion | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ | **142.48** | 💥 Exceeds (>128M) |
| **GPT-5.6-Sol** | **D (Aware)** | **T1** | In-place symmetric block loop ($B=512$), mmap read | `float32` ($32.8\text{ MB}$) | $512 \times 512 \times 4\text{ B} = 1.05\text{ MB}$ (in-place ops) | **78.09** | ✅ Within Budget |
| **GPT-5.6-Sol** | **A (Blind)** | **T2** | Row-blocked Gram ($B=512$), float64 promotion | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ | **142.53** | 💥 Exceeds (>128M) |
| **GPT-5.6-Sol** | **D (Aware)** | **T2** | In-place symmetric block loop ($B=512$), in-place clamp/sqrt | `float32` ($32.8\text{ MB}$) | $512 \times 512 \times 4\text{ B} = 1.05\text{ MB}$ | **92.48** | ✅ Within Budget |
| **GPT-5.6-Sol** | **A (Blind)** | **T3** | Row-blocked Gram ($B=512$), float64 promotion | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ | **146.44** | 💥 Exceeds (>128M) |
| **GPT-5.6-Sol** | **D (Aware)** | **T3** | Dynamic growing slice ($B=512 \times \text{end}$ where $\text{end} \rightarrow 8000$) | `float32` ($32.8\text{ MB}$) | Dynamic slice $512 \times 8000 \times 4\text{ B} = 16.4\text{ MB}$ + norms | **165.72** | 💥 Exceeds (>128M) |
| **GPT-5.6-Sol** | **A (Blind)** | **T4** | Row-blocked Gram ($B=512$), float64 promotion | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ + temporaries | **186.42** | 💥 Exceeds (>128M) |
| **GPT-5.6-Sol** | **D (Aware)** | **T4** | In-place symmetric block loop ($B=512$), in-place sqrt | `float32` ($32.8\text{ MB}$) | $512 \times 512 \times 4\text{ B} = 1.05\text{ MB}$ | **77.98** | ✅ Within Budget |
| **GPT-5.6-Sol** | **A (Blind)** | **T5** | Row-blocked Gram ($B=512$), float64 promotion | `float64` ($65.5\text{ MB}$) | $512 \times 8000 \times 8\text{ B} = 32.8\text{ MB}$ + temporaries | **195.36** | 💥 Exceeds (>128M) |
| **GPT-5.6-Sol** | **D (Aware)** | **T5** | In-place symmetric block loop ($B=512$), in-place sqrt | `float32` ($32.8\text{ MB}$) | $512 \times 512 \times 4\text{ B} = 1.05\text{ MB}$ | **78.56** | ✅ Within Budget |

---

## 2. Key Algorithmic Takeaways

1. **Precision Prior Discarded**: In all 10 Blind trials across both models, the generated code upcast the input matrix to `float64` ($65.5\text{ MB}$), causing base memory to double before computation started. In 10/10 Aware trials, models preserved `float32` precision.
2. **Symmetric Decomposition**: In Condition D, models switched from rectangular ($B \times N$) evaluations to strictly upper-triangular or $2D$ symmetric block evaluations ($B \times B$), cutting transient buffer size from $32.8\text{ MB}$ down to $1.05\text{ MB} - 16.0\text{ MB}$.
3. **In-Place Reuse**: GPT-5.6-Sol in Condition D actively adopted in-place arguments (`out=...`) to avoid heap allocations.
