# Project Aether-Bus: Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Target-Venue](https://img.shields.io/badge/Target-MLSys%20%2F%20OSDI-red.svg)](https://mlsys.org)
[![Sandboxing](https://img.shields.io/badge/Sandbox-Linux%20cgroup%20v2%20(128MB)-orange.svg)](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
[![Models](https://img.shields.io/badge/Models-Gemini%20%7C%20Claude%20%7C%20GPT--4o%20%7C%20DeepSeek-green.svg)](https://deepmind.google/technologies/gemini/)

> **Research Thesis:** Autonomous coding agents suffer from **"Silicon Blindness"**—they treat execution sandboxes as infinite black boxes, causing eager memory allocations, kernel Out-of-Memory (OOM) `SIGKILL`s (Exit 137), and token-wasting retry loops. By projecting physical hardware telemetry (RAM limits, CPU quotas, PSI) directly into the agent's inference state, **SCAC enables zero-shot selection of Pareto-optimal, memory-bounded algorithms on the first attempt.**

---

## 🚀 Key Experimental Highlights

```
                       THE TELEMETRY DIMENSIONALITY HIERARCHY
┌────────────────────┬─────────────────────────────┬───────────────────────────┬──────────────────────────────┐
│ Telemetry Level    │ Prompt Condition            │ Algorithmic Behavior      │ Empirical Outcome (128MB Cap)│
├────────────────────┼─────────────────────────────┼───────────────────────────┼──────────────────────────────┤
│ 0D (Blind)         │ Task only                   │ Eager full-matrix matmul  │ ❌ SIGKILL OOM (Exit 137)    │
│ Natural Language   │ "Make it memory efficient"  │ Vague scalar loops        │ ❌ Wall-Clock Timeout (>10s) │
│ 1D (RAM only)      │ `RAM limit: 128 MB`         │ Naive row-by-row norm     │ ⚠️ Timeout (>10s, too slow)  │
│ 2D (RAM + CPU)     │ `RAM: 128MB, CPU: 10s`      │ 2D Block Tiling (B=2000)  │ ✅ 0.63s, 69.8 MB (PARETO)   │
│ 1D (2GB Ceiling)   │ `RAM limit: 2 GB`           │ Symmetric full matmul     │ ⚠️ Over-allocation (512MB)   │
└────────────────────┴─────────────────────────────┴───────────────────────────┴──────────────────────────────┘
```

### 📊 Benchmark Summary

| Experiment Phase | Task Description | Blind (0D) Result | Aware (2D SCAC) Result | Empirical Gain |
|---|---|---|---|---|
| **Phase 1: CSV Aggregation** | 85MB raw CSV group-by aggregation under 128MB cgroup v2 | 6/9 trials used eager unconstrained reads | **100% chunked/streaming reads** | **66.7% optimization shift, 2.22x speedup** |
| **Phase 2: Euclidean Distance** | $8000 \times 1024$ float32 pairwise distance ($\sum \|v_i - v_j\|_2$) | **SIGKILL Exit 137** (Allocated >512MB intermediate) | **Exit 0 Success** ($32.03\text{ MB}$ peak RSS, $0.63\text{s}$) | **OOM Elimination (0% $\rightarrow$ 100% First-Pass Pass Rate)** |
| **Local Prompt Ablation** | 4-variant boundary sensitivity study | Naive eager matmul | **SOTA 2D Block Tiling ($B=2000$)** | **Proves Quantitative Sensitivity over NL advice** |

---

## 🏛️ System Architecture: 4-Dimensional Self-Telemetry (4D-SST)

SCAC formalizes a four-dimensional telemetry vector projected into the agent inference context:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 4D SUBSTRATE & SELF-TELEMETRY AGENT (SST)                   │
│                                                                             │
│ 1. SUBSTRATE CONSTRAINTS     2. TOKEN & CONTEXT ECONOMICS                   │
│ • RAM Ceiling (`MemoryMax`)   • Remaining Context Window & Token Velocity    │
│ • CPU Quotas & Throttling     • API Rate Limit Headroom (TPM / RPM)         │
│ • Pressure Stall Info (PSI)   • Token Cost & Prefix Cache Efficiency        │
│                                                                             │
│ 3. TOOL RELIABILITY           4. COMPUTATIONAL / TOOL DECOMPOSITION          │
│ • Real-time Tool Failure Rate • Monolithic vs. Granular Tool Cost Ratio     │
│ • Execution Latency (P50/P99) • Dynamic Tool Selection & Fallback Routing   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Structure & Key Documents

| File / Directory | Description |
|---|---|
| [`RESEARCH_ROADMAP.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/RESEARCH_ROADMAP.md) | **Master Research Specification.** Contains theoretical foundation, empirical findings, and Phase 1–3 roadmap. |
| [`EXECUTION_TRACKER.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/EXECUTION_TRACKER.md) | **Live Deployment & Execution Audit.** Tracks GCP VM provisioning, cgroup v2 configurations, and run logs. |
| [`paper_draft.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/paper_draft.md) | **Research Manuscript Draft.** 6-page paper targeting top-tier systems venues (MLSys / NeurIPS Systems). |
| [`reviewer_feedback.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/reviewer_feedback.md) | **Simulated Peer Review.** Senior Area Chair review report (Score: 6/10 $\rightarrow$ Roadmap to 8.5/10). |
| [`multi_model_benchmark.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/multi_model_benchmark.py) | **Multi-Model Evaluator.** Unified benchmark router for Gemini 3.7, Claude Sonnet/Opus, GPT-4o, and DeepSeek. |
| [`week1_foil_test.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/week1_foil_test.py) | **Phase 1 Production Harness.** 10 paired trials (20 LLM runs) on CSV processing inside 128MB cgroup v2. |
| [`week2_closed_loop_test.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/week2_closed_loop_test.py) | **Phase 2 Production Harness.** Closed-loop multi-turn kernel feedback on Euclidean distance calculations. |
| [`local_experiments/prompt_ablation_study/`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/local_experiments/prompt_ablation_study/) | **Local Ablation Suite.** Self-contained suite reproducing 4 prompt variants and memory profiling. |
| [`foil_runs/`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/foil_runs/) & [`foil_runs_euclidean/`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/foil_runs_euclidean/) | **Empirical Trial Code.** All 40 generated Python trial scripts captured during cloud execution. |
| [`.agents/skills/`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/.agents/skills/) | **Agent Customizations.** Domain skills for systems benchmarking, cgroup v2 kernel telemetry, and paper writing. |

---

## ⚡ Quickstart & Reproducibility

### 1. Local Prompt Ablation Study (Zero Cloud Cost)
Reproduce the 4-variant prompt ablation suite locally to inspect behavioral divergence:

```bash
# Clone the repository
git clone https://github.com/manu2/Context-Aware-Agent-Experiment.git
cd Context-Aware-Agent-Experiment

# Install dependencies
pip install -r requirements.txt

# Run the local reproduction suite
python3 local_experiments/prompt_ablation_study/reproduce_ablation_study.py
```

### 2. Multi-Model Benchmark Execution
Run multi-model evaluations across different frontier model families:

```bash
# Evaluate with Gemini 3.7 Flash
export GEMINI_API_KEY="your-gemini-key"
export SCAC_MODEL="gemini-3.7-flash"
python3 multi_model_benchmark.py

# Evaluate with Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-key"
export SCAC_MODEL="claude-sonnet-4-20250514"
python3 multi_model_benchmark.py

# Evaluate with DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-key"
export SCAC_MODEL="deepseek-chat"
python3 multi_model_benchmark.py
```

### 3. Linux Kernel `cgroup v2` Sandbox Verification
Enforce strict 128MB memory ceiling and zero-swap sandbox:

```bash
# Launch test inside 128MB memory ceiling
systemd-run --user --scope \
    -p MemoryMax=128M \
    -p MemorySwapMax=0 \
    python3 script.py
```

---

## 🛣️ Research Roadmap

- [x] **Phase 1: Baseline Foil Signal Test** — Verified 66.7% optimization shift in CSV workloads.
- [x] **Phase 2: High-Dimensional Closed-Loop Benchmarks** — Proved OOM elimination in Euclidean distance.
- [x] **Phase 2.5: Prompt Sensitivity & Ablation** — Established the Telemetry Dimensionality Hierarchy.
- [ ] **Phase 3.1: Multi-Model Evaluation** — Cross-model validation on Claude, GPT-4o, and DeepSeek.
- [ ] **Phase 3.2: 15-Task Diversity Benchmark** — Expansion to Graph algorithms, Out-of-core Sorting, and Text processing.
- [ ] **Phase 3.3: Statistical Rigor** — Formal p-value hypothesis testing (Wilcoxon signed-rank, Cohen's d).
- [ ] **Phase 3.4: arXiv Preprint & Top-Tier Submission** — Publication target: MLSys 2027 / NeurIPS Systems track.

---

## 📄 Citation & License

This project is licensed under the Apache License 2.0. See [`LICENSE`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/LICENSE) for details.

```bibtex
@article{scac2026projectaether,
  title={Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC): Eliminating Silicon Blindness in Autonomous Coding Agents},
  author={Agrawal, Manu and SCAC Research Group},
  year={2026},
  journal={arXiv preprint}
}
```