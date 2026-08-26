# EXECUTION TRACKER: Live Deployment & Experiment Log

## Overall Status
- **Current Stage**: Stage 18.2 (Full Direct-API Replication)
- **Active Experiment**: Protocol v1.2 is active, preflight-validated, and atomically reserves each trial ID before generation. The next operational batch is three A/D pairs for each active direct-API model: Claude `rep04`–`rep06`, GPT `rep02`–`rep04`, and Gemini `rep02`–`rep04`.

## Active Replication Pair Ledger

**Counting rule:** A *pair* is one blind (A) and one telemetry (D) generation.
Historical, proxy/subagent, and fresh direct-API cohorts remain separately labeled;
this ledger is a progress plan, not permission to silently pool them into one
statistical sample.

| Model | Historical evidence retained | Fresh direct-API pairs complete | Current usable total for planning | Next three pairs | Notes |
|---|---|---:|---:|---|---|
| Claude Opus 5 | 5 canonical pairs in `experiments/05_paired_statistical_trials/` | 2 (`rep02`, `rep03`) | 7 | `rep04`, `rep05`, `rep06` | `rep01` remains preserved but excluded after the duplicate blind launch; `rep06` is its documented replacement. |
| GPT-5.6-Sol | 5 historical direct-API pairs in `experiments/05_paired_statistical_trials/` | 1 archived here (`rep01`) + 1 earlier direct-API pair confirmed by project owner | 7 | `rep02`, `rep03`, `rep04` | The earlier direct pair must be linked into the repository inventory before manuscript revision; it is counted for the operational 10-pair target, not silently merged into a fresh-only analysis. |
| Gemini | Historical task cohorts: 9 cgroup pairs (Phase 1, Gemini 3.6) and 10 cgroup pairs (Phase 2, Gemini 2.5); see notes below | 1 (`rep01`) | No single merged N: task/model/provenance differ | `rep02`, `rep03`, `rep04` | Historical Gemini evidence is retained and reported separately. Its Phase 2 summary/result inconsistency must be reconciled before quantitative manuscript use. |

### Gemini historical evidence notes

- Phase 1: 9 complete pairs on the CSV task with `gemini-3.6-flash` and enforced
  cgroup v2 limits (`docs/01_phase1_gemini_csv_report.md`).
- Phase 2: 10 generated A/B script pairs on the Euclidean task with
  `gemini-2.5-flash` via Vertex AI (`experiments/02_euclidean_gce_phase2/`).
  Its `results.json` and prose report currently disagree on aware-condition outcome
  counts; preserve the artifacts but reconcile this before calculating/reporting an
  aggregate from that cohort.
- Fresh replication: direct `gemini-3.7-flash` API calls under the frozen v1.2
  manifest. These are a new, separately reported cohort.

### Active batch: nine direct-API pairs (protocol v1.2)

| Model | Pair ID | Status | Result / artifact |
|---|---|---|---|
| Claude Opus 5 | `opus_rep04_A/D` | ⚠️ Complete | A: Python 3.10 union-type syntax failed under pinned Python 3.9.6 (exit 1; incorrect). D: correct, 105.56 MB, 0.4011 s. |
| Claude Opus 5 | `opus_rep05_A/D` | ✅ Complete | A: correct, 345.33 MB, 0.6912 s. D: correct, 111.86 MB, 0.3462 s. |
| Claude Opus 5 | `opus_rep06_A/D` | ⏳ Pending | — |
| GPT-5.6-Sol | `gpt_rep02_A/D` | ⏳ Pending | — |
| GPT-5.6-Sol | `gpt_rep03_A/D` | ⏳ Pending | — |
| GPT-5.6-Sol | `gpt_rep04_A/D` | ⏳ Pending | — |
| Gemini 3.7 Flash | `gemini_rep02_A/D` | ⏳ Pending | — |
| Gemini 3.7 Flash | `gemini_rep03_A/D` | ⏳ Pending | — |
| Gemini 3.7 Flash | `gemini_rep04_A/D` | ⏳ Pending | — |

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
| **18.1** | Direct-API Pilot Integrity Guard | `docs/07_direct_api_pilot_report.md` | ✅ **DONE** | Three clean direct-API A/D pairs completed: Claude `rep02`, GPT `rep01`, and Gemini `rep01`. All scripts were correct; observed MaxRSS fell by 47.8%, 41.8%, and 59.2%, respectively. The duplicate `opus_rep01` pair remains excluded and the runner now rejects overwrite attempts before API calls |
| **18.2** | Full Direct-API Replication Restart | `experiments/06_replication/RUN_MANIFEST.json` | 🔄 **IN PROGRESS** | Protocol v1.2 atomically reserves trial IDs before generation and writes durable failure metadata if a query fails. Clean Claude `rep03` completed correctly (168.59 MB blind → 102.80 MB telemetry). The live pair ledger above records the agreed next three-pair batch for all models and keeps historical/direct/proxy cohorts explicit |
