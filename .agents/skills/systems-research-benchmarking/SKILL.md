---
name: systems-research-benchmarking
description: >-
  SOTA empirical benchmarking protocol for Systems & GenAI research.
  Use when designing experimental harnesses, running paired A/B trials,
  computing statistical significance (paired t-test, Wilcoxon signed-rank, Cohen's d),
  profiling memory RSS/heap allocations, and measuring execution latency distribution (P50/P90/P99).
---

# Systems & GenAI Empirical Benchmarking (SOTA Protocol)

This skill provides industry-standard guidelines for running statistically rigorous, reproducible systems and GenAI experiments.

---

## 1. Experimental Design & Paired A/B Testing

### 1.1 Confound Elimination
- **Model Parameters**: Lock temperature (e.g. `0.2`), seed (where applicable), top_p, and model version (`gemini-3.7-flash`).
- **Workspace Isolation**: Symlink or copy fresh dataset instances per trial to prevent state pollution.
- **Pacing**: Introduce fixed inter-trial delays (e.g. 1.0s) to prevent API rate-limit throttling (HTTP 429) from biasing wall-clock timing.

### 1.2 Sample Size & Statistical Significance
For LLM strategy divergence and execution success comparisons:
- **Minimum Trials**: 10 paired trials (20 generations) for initial signal detection; 30–50 paired trials for paper-grade statistical power.
- **Statistical Tests**:
  - **Categorical Outcomes (Success vs. OOM)**: McNemar's Test for paired nominal data.
  - **Strategy Divergence Rate**: Binomial confidence intervals (Wilson score interval).
  - **Latency/Execution Time**: Paired t-test (parametric) or Wilcoxon signed-rank test (non-parametric).
  - **Effect Size**: Cohen's $d$ for continuous timing/memory metrics.

---

## 2. Resource Telemetry & Profiling

### 2.1 Linux Memory Profiling
- **Resident Set Size (RSS)**: Monitor peak RSS via `/proc/<pid>/status` (`VmHWM`) or `time -v`.
- **Heap Allocation**: Profile Python object allocation via `tracemalloc` to pinpoint Pandas vs PyArrow vs native object overhead.
- **cgroup v2 Memory Events**: Track `/sys/fs/cgroup/<unit>/memory.events` (`high`, `max`, `oom`, `oom_kill`).

### 2.2 Latency Profiling
Measure wall-clock latency with high-precision monotonic timers (`time.perf_counter()`):
- **P50 (Median)**: Typical execution throughput.
- **P90 / P99**: Tail latency induced by garbage collection or kernel memory reclamation pressure.

---

## 3. Data Export & Verification Standards

- **Raw Artifact Retention**: Always save raw generated Python scripts (`trial_XX_A.py`, `trial_XX_B.py`) alongside stdout/stderr outputs.
- **Structured JSON Artifact**: Export `results.json` containing trial-by-trial raw metrics, wall times, exit codes, and heuristic strategy classifications.
- **Summary Report**: Generate markdown comparison tables (`summary_report.md`) detailing success rate percentages, OOM counts, and strategy divergence rates.
