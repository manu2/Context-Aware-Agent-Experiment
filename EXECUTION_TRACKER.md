# EXECUTION TRACKER: Live Deployment & Experiment Log

## Overall Status
- **Current Stage**: Stage 21.0 (Dynamic SCAC telemetry design complete)
- **Active Experiment**: All 16 protocol-v1.2 manifest pairs have terminal archived
  artifacts. Fifteen included direct-API pairs are available for separately labelled
  cohort analysis; one Claude blind member is a retained runtime-compatibility failure and
  `opus_rep01` remains excluded because of its pre-guard duplicate launch. Protocol
  v1.2 remains frozen; the locally canonical manuscript now reflects the complete
  fresh cohort and remains under author/affiliation clearance.
- **Separate boundary extension:** Five GPT `96 MB + 10 s` aware generations are
  locally profiled under protocol `96mb-local-sweep-v1.3`. They are all correct and
  observed below 96 MB; the result is a condition-level adaptation comparison, not
  a cgroup-survival claim or a pooled cohort.
- **Boundary extension complete:** Five executable `96 MB + 10 s` aware
  generations per model are profiled locally. Correct-and-observed-`<=96 MB` is
  GPT 5/5, Claude 4/5, and Gemini 3/5. Two malformed Claude provider responses
  are retained and transparently replaced under manifest v1.5 before replacement
  generation; the reference cohorts remain separately labelled.
- **Next research phase:** ContractBench is planned as a new, frozen FSE-oriented
  benchmark rather than an extension or pooled reanalysis of the arXiv cohort.
  Its protocol is [`docs/14_fse_contractbench_protocol.md`](docs/14_fse_contractbench_protocol.md).
  The next authorized work is zero-cost task design, container/evaluator build,
  and context-isolated review; no provider generation is authorized until the
  protocol's calibration and pilot gates pass.
- **Dynamic-loop design (2026-08-28):** A research-and-strategy whitepaper now
  specifies the Phase 2 closed-loop control plane, 4D SST schema, prior-art
  boundary, three deterministic scenarios, information controls, metrics, and
  gated implementation plan. This is a design artifact only; it adds no empirical
  observations and authorizes no provider calls. See
  [`docs/15_dynamic_agent_telemetry_whitepaper.md`](docs/15_dynamic_agent_telemetry_whitepaper.md).
- **Consolidation and repository decision (2026-08-28):** Two independently
  produced Phase 2 drafts were reconciled. The evidence-audited document is now
  canonical; the narrative draft is retained with a superseded provenance banner.
  The protocol remains here, while executable harness development is planned for
  a separate repository with pinned reciprocal provenance. No repository has been
  created and no artifacts have been moved.

## Active Replication Pair Ledger

**Counting rule:** A *pair* is one blind (A) and one telemetry (D) generation.
Historical, proxy/subagent, and fresh direct-API cohorts remain separately labeled;
this ledger is a progress plan, not permission to silently pool them into one
statistical sample.

| Model | Historical evidence retained | Fresh direct-API pairs complete | Current usable total for planning | Next three pairs | Notes |
|---|---|---:|---:|---|---|
| Claude Opus 5 | 5 canonical pairs in `experiments/05_paired_statistical_trials/` | 5 (`rep02`–`rep06`) | 10, only as separately labelled historical and fresh cohorts | Complete | `rep04_A` is retained as an execution failure; all five D scripts are correct and under 128 MB. `rep01` remains preserved but excluded after the duplicate blind launch. |
| GPT-5.6-Sol | 5 historical direct-API pairs in `experiments/05_paired_statistical_trials/` | 5 archived here (`rep01`–`rep05`) | 10, only as separately labelled historical and fresh cohorts | Complete | The project-owner-confirmed earlier direct pair still needs an artifact location before it can appear in any numeric analysis. |
| Gemini | Historical task cohorts: 9 cgroup pairs (Phase 1, Gemini 3.6) and 10 cgroup pairs (Phase 2, Gemini 2.5); see notes below | 5 (`rep01`–`rep05`) | No single merged N: task/model/provenance differ | Complete | Historical Gemini evidence is retained and reported separately. Its Phase 2 summary/result inconsistency must be reconciled before quantitative manuscript use. |

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

### Completed direct-API campaign (protocol v1.2)

| Model | Pair ID | Status | Result / artifact |
|---|---|---|---|
| Claude Opus 5 | `opus_rep04_A/D` | ⚠️ Complete | A: Python 3.10 union-type annotation caused a runtime compatibility failure under pinned Python 3.9.6 (exit 1; incorrect). D: correct, 105.56 MB, 0.4011 s. |
| Claude Opus 5 | `opus_rep05_A/D` | ✅ Complete | A: correct, 345.33 MB, 0.6912 s. D: correct, 111.86 MB, 0.3462 s. |
| Claude Opus 5 | `opus_rep06_A/D` | ✅ Complete | A: correct, 305.97 MB, 1.3413 s. D: correct, 111.38 MB, 0.4020 s. |
| GPT-5.6-Sol | `gpt_rep02_A/D` | ✅ Complete | A: correct, 179.92 MB, 0.6274 s. D: correct, 60.00 MB, 0.3485 s. |
| GPT-5.6-Sol | `gpt_rep03_A/D` | ✅ Complete | A: correct, 113.53 MB, 0.6817 s. D: correct, 54.20 MB, 0.3392 s. |
| GPT-5.6-Sol | `gpt_rep04_A/D` | ✅ Complete | A: correct, 65.70 MB, 0.2855 s. D: correct, 87.64 MB, 0.3265 s (telemetry higher RSS in this pair). |
| GPT-5.6-Sol | `gpt_rep05_A/D` | ✅ Complete | A: correct, 120.92 MB, 0.5629 s. D: correct, 55.38 MB, 0.2811 s. |
| Gemini 3.7 Flash | `gemini_rep02_A/D` | ✅ Complete | A: correct, 367.06 MB, 1.2035 s. D: correct, 170.31 MB, 0.3927 s (lower RSS but above 128 MB). |
| Gemini 3.7 Flash | `gemini_rep03_A/D` | ✅ Complete | A: correct, 671.52 MB, 0.8556 s. D: correct, 216.05 MB, 0.3125 s (lower RSS but above 128 MB). |
| Gemini 3.7 Flash | `gemini_rep04_A/D` | ✅ Complete | A: correct, 549.95 MB, 1.2158 s. D: correct, 114.34 MB, 0.3042 s. |
| Gemini 3.7 Flash | `gemini_rep05_A/D` | ✅ Complete | A: correct, 366.89 MB, 1.0606 s. D: correct, 165.19 MB, 0.3319 s (lower RSS but above 128 MB). |

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
| **10.0** | Local Prompt Ablation Study | `experiments/03_prompt_ablation_local/` | ✅ **DONE** | Exploratory four-prompt sensitivity screen; its initial memory values are not the canonical replicated MaxRSS evidence. |
| **11.0** | Senior Peer Reviewer Simulation | `benchmarks/run_peer_reviewer.py` | ✅ **DONE** | Identified roadmap for multi-model rigor and statistical variance |
| **12.0** | Anthropic Claude Sonnet 5 Suite | `experiments/04_frontier_model_benchmark/` | ✅ **DONE** | Proved block-size reduction ($B=1000 \rightarrow 500$, 215MB OOM $\rightarrow$ 92MB Pass) |
| **13.0** | OpenAI GPT-5.6-Sol Suite | `experiments/04_frontier_model_benchmark/` | ✅ **DONE** | Proved SOTA in-place buffer recycling ($4.12\text{ MB} / 0.1896\text{s}$) |
| **14.0** | Anthropic Claude Opus 5 Suite | `docs/05_claude_opus_analysis_report.md` | ✅ **DONE** | Unconditioned Blind allocates 163MB (OOM); Telemetry induces 61MB / 0.394s |
| **15.0** | Canonical 5-Paired MaxRSS Profiling | `experiments/05_paired_statistical_trials/` | ✅ **DONE** | Canonical MaxRSS dataset generated; Opus 5 (238MB -> 93MB), GPT-5.6-Sol (162MB -> 98MB) |
| **16.0** | Repository Reorganization & Provenance Lock | `benchmarks/`, `data/`, `docs/`, `experiments/` | ✅ **DONE** | Canonical dataset, profiler script, and numerical audit runner committed |
| **17.0** | Historical Manuscript Numerical Audit | `paper_draft.md` | ✅ **DONE** | The local checker verifies the historical Table 1 numbers against canonical JSON. A final manuscript revision remains required for the complete direct cohort, bibliography corrections, and Phase 2 reconciliation. |
| **17.1** | Exploratory Proxy-Pilot Provenance Cleanup | `experiments/06_replication/raw/*/*/profile.json` | ✅ **DONE** | Archived prompt hashes and standalone profiles for six proxy scripts; synchronized MaxRSS documentation with the wrapper's `RUSAGE_CHILDREN` measurement; excluded proxy pilot from primary API-model evidence |
| **18.0** | Direct-API Launch Compatibility Repair | `experiments/06_replication/RUN_MANIFEST.json` | ✅ **READY** | Verified exact model IDs with authenticated read-only requests; protocol v1.1 records Claude Opus 5's provider-required default sampling after an HTTP 400 before generation; all local preflight assertions pass |
| **18.1** | Direct-API Pilot Integrity Guard | `docs/07_direct_api_pilot_report.md` | ✅ **DONE** | Three clean direct-API A/D pairs completed: Claude `rep02`, GPT `rep01`, and Gemini `rep01`. All scripts were correct; observed MaxRSS fell by 47.8%, 41.8%, and 59.2%, respectively. The duplicate `opus_rep01` pair remains excluded and the runner now rejects overwrite attempts before API calls |
| **18.2** | Full Direct-API Replication | `docs/10_direct_api_cohort_analysis.md` | ✅ **DONE** | All 32 manifest executions have terminal artifacts. Fifteen included pairs are analyzed separately: Claude fresh 0/5 versus 5/5 observed-budget compliance (with one retained blind runtime-compatibility failure), GPT 4/5 lower-RSS pairs with one regression, and Gemini 5/5 lower-RSS pairs but 2/5 telemetry observed-budget compliance. No manuscript edits were made. |
| **18.3** | 96 MB Boundary-Sensitivity Extension | `experiments/08_96mb_cgroup_pilot/LOCAL_SWEEP_REPORT.md` | ✅ **DONE** | New 96 MB-aware local cohorts: GPT mean 60.88 MB (5/5 correct <=96), Claude 87.57 MB (4/5), Gemini 118.46 MB (3/5). Two malformed Claude responses are preserved; v1.5 predeclared identical-prompt replacements. The earlier enforced-cgroup pair is a separate operational diagnostic. |
| **19.0** | Manuscript evidence-package closure | `docs/13_fresh_code_transformation_audit.md`, `paper/figures/` | ✅ **DONE** | Generated a 45-record source-linked audit (30 fresh 128 MB scripts and 15 retained executable 96 MB scripts), machine-readable JSON with source hashes/evidence lines, and two reproducible vector figures sourced from archived metadata. The working manuscript revision and README now lead with the fresh cohort and explicit evidence boundary. |
| **19.1** | Local canonical manuscript promotion | `paper_draft.md` | ✅ **DONE** | Promoted the reviewed v3 manuscript with the independent-author block, current paired and boundary-sensitivity tables, related work, and both vector-figure references. Earlier working drafts remain preserved. Paper clearance and any code/artifact-release decision remain separate. |
| **20.0** | ContractBench FSE expansion design | `docs/14_fse_contractbench_protocol.md` | 🔄 **IN PROGRESS** | Frozen planning protocol for a new multi-environment operational-contract benchmark: numerical resources, streaming ETL, and runtime/dependency compatibility. Start with context-isolated review and local calibration; do not generate provider trials before G0/G1. |
| **21.0** | Dynamic SCAC telemetry design and consolidation | `docs/15_dynamic_agent_telemetry_whitepaper.md` | ✅ **DONE** | Consolidated two independent drafts into one canonical, evidence-audited design with a versioned 4D state, dual-tier injection, ToolRoute/MemoryGovernor/RetryBudget scenarios, causal controls, statistics, fail-closed gates, and a separate-repository implementation decision. The earlier draft remains preserved. |

### Manuscript-closure status (2026-08-27)

- **Closed from existing artifacts:** fresh row-level code audit, observed-RSS
  figures, retry-policy disclosure, deterministic data-generation command,
  updated reproducibility instructions, and scope/measurement language.
- **Still user-owned before submission:** complete accurate consenting author
  names and affiliations; a final TeX/PDF render in an arXiv-compatible toolchain.
- **Transparent immutable limitation:** provider-facing configured model IDs are
  archived, but immutable provider weight snapshots, request identifiers, and
  per-attempt request logs are not available for the completed runs.
- **Software-substrate illustration:** `opus_rep04_A` is recorded as a Python 3.9
  runtime-compatibility failure caused by a generated Python 3.10-style union
  annotation. It is an illustrative observed incident, not a tested
  runtime-version-disclosure treatment effect; the working paper lists that as
  future controlled work.
- **Manuscript review status:** the next pass is manuscript-only: strengthen the
  positive narrative and related work without adding unsupported mechanism or
  model-family claims.
- **arXiv preprint v7 revision (2026-09-03):** `paper_draft.md` now records the
  completed manuscript-only revision: the single-turn experimental unit,
  independent condition cohorts, exact measurement semantics, response handling,
  and artifact availability are explicit. Figure 1 now compares within-model
  normalized condition cohorts without implying statistical matching; Table 1 and
  Appendix A retain the native MiB outcomes. No model generations or archived
  results were changed. The frozen checklist is
  [`docs/16_arxiv_preprint_v7_revision_plan.md`](docs/16_arxiv_preprint_v7_revision_plan.md).
  The final review and submission PDFs are locally generated, ignored artifacts,
  while `paper_draft.md`, checked-in vector figures, and the renderer are versioned.
- **Final v7 polish (2026-09-04):** The manuscript now explicitly identifies
  single-turn code generation as the implementation-selection primitive and the
  numerical task as an inspectable deterministic micro-benchmark. Redundant
  introduction framing and an ambiguous related-work antecedent were removed. The
  review-PDF renderer now protects widows/orphans and uses dedicated white header
  cells with proportional table columns. No empirical artifact, result, or claim
  boundary changed.
- **Submission-PDF preflight (2026-09-04):** Fixed multi-line Markdown bullet
  parsing in the PDF renderer so every contribution item is a single,
  correctly wrapped paragraph. Rebuilt the standalone PDF with embedded Arial and
  Courier New TrueType fonts; it is eight pages, searchable, contains no
  JavaScript or encryption, and passed the complete manuscript-evidence verifier.
  No manuscript text, experimental result, or claim changed.
- **Submission-PDF figure quality (2026-09-04):** Replaced the environment-dependent
  low-resolution figure-preview fallback with native-vector drawing from the
  checked-in figure definitions. The renderer preserves each figure's native
  aspect ratio; Figure 2 is no longer vertically compressed. The final PDF contains
  zero raster image objects and retains embedded manuscript fonts.
