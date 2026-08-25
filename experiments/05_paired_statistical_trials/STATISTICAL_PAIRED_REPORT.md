# Canonical Paired Trial Report: Substrate-Aware Code Generation

**Dataset**: [`experiments/05_paired_statistical_trials/canonical_paired_results.json`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/05_paired_statistical_trials/canonical_paired_results.json)  
**Profiler**: [`experiments/05_paired_statistical_trials/profile_canonical_maxrss.py`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/05_paired_statistical_trials/profile_canonical_maxrss.py)  
**Methodology**: Isolated subprocess execution measuring true OS Peak Resident Set Size (`resource.getrusage(RUSAGE_SELF).ru_maxrss`).

---

## 1. Primary Empirical Evidence (N=5 Paired Runs)

```
======================================================================================================================
Table 1: Paired Substrate-Awareness Evaluation (Post-Hoc OS MaxRSS Profiling of Archived Scripts)
======================================================================================================================
Model & Trial      | Condition A: Blind MaxRSS | Condition D: Aware MaxRSS | Blind 128M Budget | Aware 128M Budget
----------------------------------------------------------------------------------------------------------------------
claude-opus-5 (T1) |         205.69 MB         |          82.48 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.270s)
claude-opus-5 (T2) |         162.95 MB         |          99.17 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.255s)
claude-opus-5 (T3) |         239.75 MB         |         104.38 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.244s)
claude-opus-5 (T4) |         291.78 MB         |          91.34 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.260s)
claude-opus-5 (T5) |         291.83 MB         |          90.47 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.310s)
----------------------------------------------------------------------------------------------------------------------
--> claude-opus-5 Aggregate:
    Peak MaxRSS:   Blind = 238.40 ± 49.94 MB   vs.   Aware =  93.57 ±  7.56 MB (2.55x Reduction)
    Wall Latency:  Blind =  0.7119 ±  0.2293s   vs.   Aware =  0.2677 ±  0.0228s (2.66x Speedup)
    128M Budget Compliance:       Blind = 0/5 (0%)    vs.   Aware = 5/5 (100%)
======================================================================================================================
gpt-5.6-sol   (T1) |         142.48 MB         |          78.09 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.255s)
gpt-5.6-sol   (T2) |         142.53 MB         |          92.48 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.283s)
gpt-5.6-sol   (T3) |         146.44 MB         |         165.72 MB         | 💥 Exceeds (>128M)| 💥 Exceeds (166 MB)
gpt-5.6-sol   (T4) |         186.42 MB         |          77.98 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.262s)
gpt-5.6-sol   (T5) |         195.36 MB         |          78.56 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.247s)
----------------------------------------------------------------------------------------------------------------------
--> gpt-5.6-sol Aggregate:
    Peak MaxRSS:   Blind = 162.65 ± 23.28 MB   vs.   Aware =  98.57 ± 34.03 MB (1.65x Reduction)
    Wall Latency:  Blind =  0.5690 ±  0.0061s   vs.   Aware =  0.2608 ±  0.0121s (2.18x Speedup)
    128M Budget Compliance:       Blind = 0/5 (0%)    vs.   Aware = 4/5 (80%)
======================================================================================================================
```

---

## 2. Key Findings & Behavioral Observations

1. **Claude Opus 5**:
   * **Blind Condition**: Promotes array to `float64` and computes full rectangular matrix products, resulting in peak MaxRSS of $238.40 \pm 49.94\text{ MB}$ ($5/5$ exceeding 128 MB budget).
   * **Substrate-Aware Condition**: Retains `float32` and computes upper-trapezoid matrix products, reducing peak MaxRSS to $93.57 \pm 7.56\text{ MB}$ ($5/5$ remaining under 128 MB budget) with a $2.66\times$ speedup ($0.2677\text{s}$).

2. **GPT-5.6-Sol**:
   * **Blind Condition**: Uses full-matrix operations, consuming $162.65 \pm 23.28\text{ MB}$ ($5/5$ exceeding 128 MB budget).
   * **Substrate-Aware Condition**: Uses memory-mapped I/O and in-place distance clamping/sqrt, reducing average MaxRSS to $98.57 \pm 34.03\text{ MB}$ ($4/5$ remaining under 128 MB budget) with a $2.18\times$ speedup ($0.2608\text{s}$).
   * **Imperfect Constraint Reasoning**: Trial 3 exceeded 128 MB at $165.72\text{ MB}$, demonstrating that substrate disclosure does not guarantee 100% compliance across all stochastic runs.
