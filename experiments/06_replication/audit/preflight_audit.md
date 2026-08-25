# Preflight Audit: Historical Experiment Evaluation & Methodological Baseline

**Date:** August 2026  
**Artifact Scope:** Authoritative preflight audit for the Substrate-Aware Code Generation experiment before replication freeze.  

---

## 1. What is Definitely Correct

1. **The Core Physical Finding**:
   * Blind agents consistently promote inputs to `float64` and evaluate rectangular blocks ($B \times N$), resulting in measured MaxRSS of **$142\text{ MB} - 314\text{ MB}$** (exceeding 128 MB in 10/10 trials).
   * Substrate-aware agents retain `float32`, evaluate symmetric upper blocks ($B \times B$), and reuse memory, achieving measured MaxRSS of **$78\text{ MB} - 104\text{ MB}$** (budget compliant in 9/10 trials).
2. **Canonical Data Integrity**:
   * All 20 archived trial scripts in `experiments/05_paired_statistical_trials/runs/` are genuine, executable, and traceable.
   * `profile_canonical_maxrss.py` executes each script in an isolated child subprocess, measuring true OS `resource.getrusage(RUSAGE_SELF).ru_maxrss`.
3. **Statistical Calculations**:
   * All reported means, standard deviations, speedup ratios, and reduction ratios in `paper_draft.md` Table 1 and Section 3.1 match `canonical_paired_results.json` exactly.
4. **Selfcheck Ablation Robustness**:
   * Removing `selfcheck` from Opus Trial 1 changes MaxRSS from $205.69\text{ MB}$ to $196.04\text{ MB}$ (-4.7%), shifting the overall Opus Blind mean by only $-1.93\text{ MB}$ ($0.81\%$) and leaving budget compliance unchanged ($0/5$).

---

## 2. What Was Objectively Inaccurate & Fixed

1. **Table 2 Cell Discrepancies**:
   * Previous draft had copy-pasted numbers from Table 1 Trial 1 into exploratory Table 2. **Fixed**: Replaced with exact values from audited JSON logs.
2. **Historical Tracemalloc vs. MaxRSS Ambiguity**:
   * Early reports used Python `tracemalloc` without clarifying it missed C-extension heap allocations. **Fixed**: Added prominent historical/methodology notice headers across `docs/` and `experiments/`.
3. **Section 4.1 Opus Code Snippet**:
   * Previously showed handwritten illustration. **Fixed**: Aligned with exact `BLOCK=2000` Python code from `claude-opus-5_trial1_D_2Dtelemetry.py`.
4. **Citations Audited**:
   * Verified and corrected all 8 references (AgentSight arXiv:2508.02736, RLEF arXiv:2410.02089, SafeCodeRL Sensors 2026).

---

## 3. What Must Be Fixed Before Replication Execution

1. **Frozen Task Specification (`TASK.md`)**:
   * Lock exact task prompt text, input array dimensions, and SHA-256 hash.
2. **Frozen Condition Definitions (`CONDITIONS.md`)**:
   * Enforce that Condition A (Blind) and Condition D (Aware) differ **solely** by the 2-line execution limit string.
3. **Frozen Measurement Specification (`MEASUREMENT_SPEC.md`)**:
   * Standardize post-hoc OS-level MaxRSS and wall-clock latency measurement via `resource.getrusage`.
4. **Frozen Run Manifest (`RUN_MANIFEST.json`)**:
   * Assign all 30 immutable trial IDs (15 pairs across 3 models) before execution.

---

## 4. Methodological Limitations (Kept Transparent)

1. **Post-Hoc Measurement**: MaxRSS is measured via post-hoc isolated subprocess execution rather than native cgroup kernel enforcement during inference.
2. **Model Identifier Aliases**: Frontier model aliases (e.g. `claude-opus-5`, `gpt-5.6-sol`, `gemini-3.7-flash`) must be transparently documented alongside commercial API equivalents.

---

## 5. Issues for Human Decision

1. **API Endpoints for Live Replication**: Confirm which live model endpoints / keys Manu wishes to query for the 30 fresh replication trials (e.g. `claude-3-7-sonnet-20250219`, `o3-mini` / `gpt-4o`, `gemini-2.0-flash` / `gemini-1.5-pro` vs internal frontier aliases).
