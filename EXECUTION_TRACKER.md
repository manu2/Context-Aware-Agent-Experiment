# EXECUTION TRACKER: Live Deployment & Experiment Log

## Overall Status
- **Current Stage**: Stage 18.0 (Direct-API Replication Launch Readiness)
- **Active Experiment**: Direct-API replication protocol v1.1 is preflight-validated. The first Claude launch was rejected before generation because Claude Opus 5 disallows explicitly supplied sampling controls; protocol v1.1 records its required provider-default sampling. No successful direct-API trial artifact exists yet.

---

## Stage Summary Table

| Stage | Name | Key Script / Artifact | Status | Key Output / Verified Result |
|---|---|---|---|---|
| **1.0** | Project Setup & Baseline Planning | `RESEARCH_ROADMAP.md` | ✅ **DONE** | 4D SST Framework defined |
| **2.0** | GCP VM Provisioning (Phase 1) | `gcloud compute instances create` | ✅ **DONE** | `e2-medium` Ubuntu 24.04 VM provisioned |
| **3.0** | Phase 1 Foil Test Execution | `benchmarks/week1_foil_test.py` | ✅ **DONE** | 9 paired CSV trials; 66.7% optimization shift; 2.22x speedup |
| **4.0** | GCP Teardown (Phase 1) | `gcloud compute instances delete` | ✅ **DONE** | Zero lingering cloud costs |
| **5.0** | Phase 1 Verification & Reporting | `docs/01_phase1_gemini_csv_report.md` | ✅ **DONE** | Fully verified empirical report |
| **6.0** | Phase 2 High-Dimensional Task Design | `data/vectors.npy` | ✅ **DONE** | 8000x1024 float32 matrix created (32.8 MB) |
| **7.0** | Local Verification (Phase 2 Single Trial) | `experiments/02_euclidean_gce_phase2/` | ✅ **DONE** | Blind: OOM (SIGKILL 137); Aware: 32.03 MB pass |
| **8.0** | GCP VM Provisioning (Phase 2) | `gcloud compute instances create` | ✅ **DONE** | `e2-medium` VM provisioned |
| **9.0** | Phase 2 10-Trial GCE Execution | `benchmarks/week2_closed_loop_test.py` | ✅ **DONE** | 10/10 OOM in Blind; 9/10 strategy shift in Aware |
| **10.0** | Local Prompt Ablation Study | `experiments/03_prompt_ablation_local/` | ✅ **DONE** | 4 prompt variants; proves 2D Block Tiling Pareto-optimality |
| **11.0** | Senior Peer Reviewer Simulation | `benchmarks/run_peer_reviewer.py` | ✅ **DONE** | Identified roadmap for multi-model rigor and statistical variance |
| **12.0** | Anthropic Claude Sonnet 5 Suite | `experiments/04_frontier_model_benchmark/` | ✅ **DONE** | Proved block-size reduction ($B=1000 \rightarrow 500$, 215MB OOM $\rightarrow$ 92MB Pass) |
| **13.0** | OpenAI GPT-5.6-Sol Suite | `experiments/04_frontier_model_benchmark/` | ✅ **DONE** | Proved SOTA in-place buffer recycling ($4.12\text{ MB} / 0.1896\text{s}$) |
| **14.0** | Anthropic Claude Opus 5 Suite | `docs/05_claude_opus_analysis_report.md` | ✅ **DONE** | Unconditioned Blind allocates 163MB (OOM); Telemetry induces 61MB / 0.394s |
| **15.0** | Canonical 5-Paired MaxRSS Profiling | `experiments/05_paired_statistical_trials/` | ✅ **DONE** | Canonical MaxRSS dataset generated; Opus 5 (238MB -> 93MB), GPT-5.6-Sol (162MB -> 98MB) |
| **16.0** | Repository Reorganization & Provenance Lock | `benchmarks/`, `data/`, `docs/`, `experiments/` | ✅ **DONE** | Canonical dataset, profiler script, and numerical audit runner committed |
| **17.0** | Master arXiv Paper Calibration | `paper_draft.md` | ✅ **DONE** | Calibrated claims, added academic references [1]-[8], verified 100% numerical match |
| **17.1** | Exploratory Proxy-Pilot Provenance Cleanup | `experiments/06_replication/raw/*/*/profile.json` | ✅ **DONE** | Archived prompt hashes and standalone profiles for six proxy scripts; synchronized MaxRSS documentation with the wrapper's `RUSAGE_CHILDREN` measurement; excluded proxy pilot from primary API-model evidence |
| **18.0** | Direct-API Launch Compatibility Repair | `experiments/06_replication/RUN_MANIFEST.json` | ✅ **READY** | Verified exact model IDs with authenticated read-only requests; protocol v1.1 records Claude Opus 5's provider-required default sampling after an HTTP 400 before generation; all local preflight assertions pass |
