# Replication Preflight Checklist & Verification Gate

**Date:** August 2026  
**Protocol Version:** 1.0 (Frozen)  

---

## 1. Experimental Integrity Assertions

- [x] **Exact Task Frozen:** `experiments/06_replication/TASK.md` created with exact wording and SHA-256 hash `199a60e06...`.
- [x] **Condition A Prompt Frozen:** `experiments/06_replication/CONDITIONS.md` contains unconditioned task text.
- [x] **Condition D Prompt Frozen:** `experiments/06_replication/CONDITIONS.md` contains 2D telemetry limits.
- [x] **A/D Parity Audited:** `experiments/06_replication/audit/condition_parity_audit.md` confirms zero algorithmic hints.
- [x] **Model IDs Verified & Documented:** `experiments/06_replication/audit/model_audit.md` records all model identifiers.
- [x] **Environment Recorded:** `experiments/06_replication/ENVIRONMENT.md` documents Darwin arm64, Python, and BLAS libraries.
- [x] **MaxRSS Measurement Validated:** `experiments/06_replication/MEASUREMENT_SPEC.md` specifies `ru_maxrss` OS process measurement.
- [x] **Wall-Clock Measurement Validated:** `time.perf_counter()` boundary specified around execution.
- [x] **128 MB Definition Frozen:** Compliance defined strictly as `MaxRSS < 128.0 MB`.
- [x] **Failure & Retry Policy Frozen:** Valid model code that crashes/OOMs is preserved as an experimental outcome; no outcome-dependent reruns.
- [x] **Raw Artifact Schema Frozen:** `experiments/06_replication/raw/<model>/<trial_id>/` layout locked.
- [x] **30 Immutable Trial IDs Generated:** `experiments/06_replication/RUN_MANIFEST.json` contains 15 matched pairs.
- [x] **No Outcome-Dependent Exclusions:** All planned trials will be reported in the post-execution report.
- [x] **Zero Manuscript Updates During Execution:** `paper_draft.md` will NOT be edited during replication.
- [x] **Zero Replication Trials Executed:** Harness is frozen without running any queries.

---

**READY FOR EXECUTION — AWAITING HUMAN APPROVAL**
