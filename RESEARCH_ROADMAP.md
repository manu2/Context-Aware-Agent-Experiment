# RESEARCH ROADMAP: Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC)

## Project Overview
Investigating whether projecting physical hardware constraints (RAM ceilings, CPU time limits) and runtime telemetry into an AI agent's inference context eliminates "Silicon Blindness" (kernel OOM kills, eager memory allocations, execution timeouts).

---

## 1. The 4-Dimensional Self-Telemetry (SST) Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    4D SELF-TELEMETRY INJECTION TUPLE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  T = < M_ceiling,  C_quota,  R_tool,  V_token >                             │
│                                                                             │
│  1. M_ceiling (Spatial):   RAM Limit & Memory Pressure (cgroup v2)          │
│  2. C_quota   (Temporal):  CPU Quota & Wall-Clock Execution Deadline        │
│  3. R_tool    (Operative): Tool Reliability Index (TRI) & P99 Latency       │
│  4. V_token   (Economic):  Context Window Consumption & Token Economics     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Research Roadmap & Milestone Tracker

### Phase 1: Zero-Middleware Foil Test (Completed ✅)
- **Workload**: Out-of-Core CSV GroupBy Aggregation (`data.csv`, 85 MB).
- **Environment**: Strict 128 MB RAM `cgroup v2` sandbox on Google Compute Engine (`e2-medium`).
- **Key Finding**: Disclosing 128 MB limit induced a **66.7% structural shift** to streaming chunked iterators (`pd.read_csv(chunksize=10000)`), achieving a **2.22x speedup** and eliminating memory kills.
- **Report**: [`docs/01_phase1_gemini_csv_report.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/01_phase1_gemini_csv_report.md)

### Phase 2: High-Dimensional Matrix Operations (Completed ✅)
- **Workload**: Pairwise Euclidean Distance on an $8,000 \times 1,024$ float32 matrix (`vectors.npy`, 32.8 MB).
- **Key Finding**: In 10 paired GCE trials, Condition A (Blind) failed with **10/10 OOM Kills (`SIGKILL 137`)**, while Condition B (Substrate-Aware) achieved **9/10 Algorithmic Strategy Shifts (90.0%)** to memory-bounded streaming.
- **Report**: [`docs/02_phase2_gemini_euclidean_report.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/02_phase2_gemini_euclidean_report.md)

### Phase 3: Multi-Model Frontier Evaluation & Statistical Validation (Completed ✅)
- **Evaluated Models**: Google `gemini-3.7-flash`, Anthropic `claude-opus-5`, OpenAI `gpt-5.6-sol`, Anthropic `claude-sonnet-5`.
- **4-Condition Ablation**: Proved quantitative boundary sensitivity and SOTA 2D Block Tiling Pareto-optimality.
- **5-Paired Statistical Trials**: Proved statistically significant memory reduction ($p < 0.01$) and elevated 128 MB First-Pass Correctness Rate (FPCR) from $40\% \rightarrow 100\%$ on `claude-opus-5` and achieved $4.72\times$ memory reduction and $1.91\times$ speedup on `gpt-5.6-sol`.
- **Reports**: [`docs/04_frontier_models_report.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/04_frontier_models_report.md), [`docs/05_claude_opus_analysis_report.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/05_claude_opus_analysis_report.md), and [`docs/06_statistical_paired_report.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/06_statistical_paired_report.md).

### Phase 4: arXiv Manuscript Filing (In Progress 🔄)
- **Primary Document**: [`paper_draft.md`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/paper_draft.md)
- **Target Category**: `cs.DC` (Distributed & Cluster Computing) / `cs.AI` (Artificial Intelligence).
- **Next Step**: Benchmark Expansion on the 3-Task Silicon Stress Suite.
- **Provenance boundary:** The archived exploratory subagent proxy pilot in `experiments/06_replication/raw/` is not primary evidence for named provider API models. Any such manuscript claim requires the frozen direct-API runner and its per-trial artifacts.

---

## 3. Specification: The 3-Task Silicon Stress Suite

For subsequent benchmark evaluations across additional models, we define the standardized 3-task suite:

| Task ID | Domain | Workload / Dataset | Memory Mechanic & OOM Trigger | Optimal Telemetry-Conditioned Strategy |
|---|---|---|---|---|
| **Task 1** | Scientific / Matrix | Pairwise Euclidean Distance ($8,000 \times 1,024$, 32.8 MB) | $O(N^2)$ broadcasting allocates 1.56 GB $\rightarrow$ OOM | Level-3 BLAS 2D Symmetric Block Tiling ($B=512-2000$) |
| **Task 2** | Data Engineering | Out-of-Core CSV GroupBy Aggregation (2,000,000 rows, 85 MB) | Eager `pd.read_csv()` allocates 240 MB $\rightarrow$ OOM | Streaming Chunked Iteration (`chunksize=10000`) |
| **Task 3** | Systems / Logs | External Frequency Top-K / Log Aggregation (200 MB text) | Full in-memory parsing allocates 350 MB $\rightarrow$ OOM | External Merge Sort / Bounded Heap Streaming |
