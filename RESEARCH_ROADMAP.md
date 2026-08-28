# RESEARCH ROADMAP: Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC)

## Project Overview

This project advances the broader thesis that **execution context is a
decision-relevant input to AI agents**. An agent that receives a task but not the
environment in which it must act is substrate-blind: its plan is not deliberately
conditioned on available memory, time, compute, tool reliability, quota, or cost.

The completed code-generation study is the first inspectable proof of concept for
this thesis. It tests whether static RAM and execution-time disclosure changes
generated numerical implementations, correctness, observed process MaxRSS, and
wall time. It does not claim to have evaluated CPU-quota, GPU/VRAM, tool-reliability,
token-economy, or dynamic-telemetry dimensions; those are planned future studies.

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
- **Report**: [`docs/01_phase1_gemini_csv_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/01_phase1_gemini_csv_report.md)

### Phase 2: High-Dimensional Matrix Operations (Completed ✅; historical result requires careful use)
- **Workload**: Pairwise Euclidean Distance on an $8,000 \times 1,024$ float32 matrix (`vectors.npy`, 32.8 MB).
- **Archived result**: In 10 paired GCE trials, Condition A recorded 10/10 OOM
  kills and Condition B recorded 9/10 strategy divergences toward row streaming.
  The raw `results.json` records **0/10 successful aware executions** (six OOM
  kills and four timeouts), even though the preceding single-trial report records
  one aware success. Do not report an aggregate Phase 2 success rate until this
  artifact/prose discrepancy is reconciled.
- **Report**: [`docs/02_phase2_gemini_euclidean_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/02_phase2_gemini_euclidean_report.md)

### Phase 3: Multi-Model Frontier Evaluation & Statistical Validation (Completed ✅)
- **Evaluated Models**: Google `gemini-3.7-flash`, Anthropic `claude-opus-5`, OpenAI `gpt-5.6-sol`, Anthropic `claude-sonnet-5`.
- **4-Condition Ablation**: Exploratory single-trial screen showing prompt-sensitive
  implementation choices; it is not a replicated model-level estimate.
- **Historical 5-pair post-hoc MaxRSS trials**: The canonical JSON reports
  descriptive reductions from 238.40 to 93.57 MB for Claude and 162.65 to 98.57
  MB for GPT, with respective observed-threshold fractions of 0/5 to 5/5 and 0/5
  to 4/5. The paper does not currently specify a valid statistical test; this
  roadmap therefore makes no significance claim from those five pairs.
- **Reports**: [`docs/04_frontier_models_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/04_frontier_models_report.md), [`docs/05_claude_opus_analysis_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/05_claude_opus_analysis_report.md), and [`docs/06_statistical_paired_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/06_statistical_paired_report.md).

### Phase 4: arXiv Manuscript Filing (In Progress 🔄)
- **Primary Document**: [`paper_draft.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/paper_draft.md)
- **Target Category**: `cs.DC` (Distributed & Cluster Computing) / `cs.AI` (Artificial Intelligence).
- **Current canonical revision (2026-08-28):** [`paper_draft.md`](paper_draft.md)
  contains the approved v6 manuscript with comparative 96 MB RSS/time presentation,
  normalized and raw-observation figures, model-configuration disclosure, and
  agent-harness framing. Earlier manuscript revisions are retained under
  [`paper/archive/manuscripts/`](paper/archive/manuscripts/).
- **Next Step**: Author review, then arXiv-compatible TeX/PDF rendering and
  internal clearance; benchmark expansion remains future research rather than a
  prerequisite to this preprint.
- **Provenance boundary:** The archived exploratory subagent proxy pilot in `experiments/06_replication/raw/` is not primary evidence for named provider API models. Any such manuscript claim requires the frozen direct-API runner and its per-trial artifacts.
- **Launch compatibility record:** Before the first successful direct-API generation, the protocol was versioned from `1.0-frozen` to `1.1-frozen`. `claude-opus-5` accepted authenticated model lookup but rejected a Messages request containing explicit non-default sampling controls; v1.1 therefore records provider-default Claude sampling, while preserving identical sampling treatment within every A/D pair. This correction does not alter the task, prompts, dataset, execution environment, or outcome measurements.
- **Pilot integrity record:** The first `opus_rep01_A` launch was unintentionally invoked twice before the runner had a write-once artifact guard; the earlier response was overwritten and cannot be analyzed. The repository retains the surviving files, excludes the affected pair from pilot inference, and uses the already-predeclared `opus_rep02_A/D` pair as the clean replacement. The runner now refuses an occupied trial directory before it sends an API request.
- **Direct-API pilot (2026-08-27):** One clean pair per model completed under protocol v1.1. All six included programs were correct; observed process MaxRSS decreased from A to D for Claude (206.02 to 107.48 MB), GPT (113.06 to 65.83 MB), and Gemini (306.38 to 124.91 MB). This pilot reports observed macOS process RSS rather than cgroup-enforced survivability and is not pooled with historical or proxy artifacts. See [`docs/07_direct_api_pilot_report.md`](docs/07_direct_api_pilot_report.md).
- **Protocol v1.2 integrity amendment:** The runner atomically reserves a trial ID before generation and persists failure metadata rather than permitting a retry to overwrite or erase an attempted run. It also adds `opus_rep06_A/D` as the documented replacement for the excluded duplicate `opus_rep01` pair. No task, prompt, dataset, model configuration, environment, or outcome measurement changed.
- **Replication progress (2026-08-27):** The first post-amendment Claude pair (`opus_rep03`) completed with correct outputs in both conditions. Observed MaxRSS was 168.59 MB in the blind condition and 102.80 MB after telemetry disclosure. This is an additional replication observation, not a manuscript-level aggregate update.
- **Live tracking rule:** `EXECUTION_TRACKER.md` is the authoritative pair-level ledger for the active direct-API campaign. It records historical, fresh direct-API, and subagent/proxy cohorts separately, updates the planned next pairs after each completed run, and never treats a planning count as a pooled statistical sample.
- **Fresh Claude cohort complete (2026-08-27):** Five direct-API pairs (`rep02`–`rep06`) are archived under protocol v1.2. In the blind condition, four scripts were functionally correct but exceeded 128 MB and one failed under Python 3.9.6; all five telemetry scripts were correct and observed below 128 MB. This is a new cohort to compare with—not silently pool into—the historical canonical cohort.
- **Complete direct-API campaign (2026-08-27):** All 32 predeclared v1.2 manifest
  executions have terminal artifacts. Excluding the pre-guard duplicate
  `opus_rep01` pair, the fresh direct cohort consists of five Claude, five GPT, and
  five Gemini pairs. Its results are recorded in
  [`docs/10_direct_api_cohort_analysis.md`](docs/10_direct_api_cohort_analysis.md)
  and will remain separate from the historical cohorts in any manuscript revision.
- **96 MB enforced-cgroup pilot (2026-08-27):** A separate GPT one-pair pilot used a
  fresh Ubuntu cgroup v2 host with `MemoryMax=96M`, `MemorySwapMax=0`, and a 10 s
  runtime limit; a 150 MB allocation positive control was OOM-killed. The blind
  script OOM-killed, while the first 96 MB-aware script timed out at 10.086 s. This
  demonstrates a changed implementation but not successful joint constraint
  satisfaction; it is paused rather than extended automatically. See
  [`experiments/08_96mb_cgroup_pilot/PILOT_PROTOCOL.md`](experiments/08_96mb_cgroup_pilot/PILOT_PROTOCOL.md).
- **96 MB local boundary-sensitivity extension (2026-08-27):** The core adaptation
  question is evaluated using local isolated-process MaxRSS rather than cgroup
  survival. Five new 96 MB-aware outputs per model were run against separately
  labelled fresh blind and 128 MB-aware reference distributions. GPT was 5/5
  correct and observed <=96 MB (mean 60.88 MB); Claude was 4/5 (87.57 MB); and
  Gemini was 3/5 (118.46 MB). All retained scripts were correct, but the latter
  two cohorts include observed-RSS boundary misses. Two malformed Claude provider
  responses were preserved and replaced only after a v1.5 manifest amendment
  predeclared identical-prompt replacements. This supports resource-relevant
  adaptation under tighter disclosure, not a deterministic or monotonic reduction
  claim. See
  [`experiments/08_96mb_cgroup_pilot/LOCAL_SWEEP_REPORT.md`](experiments/08_96mb_cgroup_pilot/LOCAL_SWEEP_REPORT.md).
- **Evidence-package closure (2026-08-27):** The revised manuscript pathway now
  includes a complete source-linked audit of 30 fresh 128 MB scripts and 15
  retained executable 96 MB scripts, its machine-readable JSON companion, and two
  reproducible vector figures generated directly from archived metadata. The
  broad thesis remains that execution context is decision-relevant agent input;
  the numerical code study is explicitly framed as a controlled proof of concept,
  not evidence that every future telemetry dimension works. See
  [`docs/13_fresh_code_transformation_audit.md`](docs/13_fresh_code_transformation_audit.md).
  The manuscript remains local during author/affiliation clearance. Remaining
  submission work is authorship plus final TeX/PDF rendering and independent
  verification, not additional empirical collection.
- **Software compatibility as a future substrate dimension:** One retained blind
  Claude script used a Python 3.10-style union annotation and failed under the
  pinned Python 3.9.6 runtime. This incident is not a causal experiment on version
  disclosure, but it supports including interpreter/runtime version as an explicit
  future execution-context dimension alongside physical resource constraints.

---

## 3. Specification: The 3-Task Silicon Stress Suite

For subsequent benchmark evaluations across additional models, we define the standardized 3-task suite:

| Task ID | Domain | Workload / Dataset | Memory Mechanic & OOM Trigger | Optimal Telemetry-Conditioned Strategy |
|---|---|---|---|---|
| **Task 1** | Scientific / Matrix | Pairwise Euclidean Distance ($8,000 \times 1,024$, 32.8 MB) | $O(N^2)$ broadcasting allocates 1.56 GB $\rightarrow$ OOM | Level-3 BLAS 2D Symmetric Block Tiling ($B=512-2000$) |
| **Task 2** | Data Engineering | Out-of-Core CSV GroupBy Aggregation (2,000,000 rows, 85 MB) | Eager `pd.read_csv()` allocates 240 MB $\rightarrow$ OOM | Streaming Chunked Iteration (`chunksize=10000`) |
| **Task 3** | Systems / Logs | External Frequency Top-K / Log Aggregation (200 MB text) | Full in-memory parsing allocates 350 MB $\rightarrow$ OOM | External Merge Sort / Bounded Heap Streaming |
