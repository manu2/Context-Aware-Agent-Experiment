# EXECUTION TRACKER: Live Deployment & Experiment Log

## Overall Status
- **Current Stage**: Stage 22.3 (AAMAS E0b and E1 complete; direct-API canary next)
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
- **Next research phase:** An AAMAS 2027 experiment-first Execution Contract Bridge
  study is planned as a new cohort rather than an extension or pooled reanalysis
  of the arXiv evidence. Its build-once vertical slice, zero-cost imported-response
  smoke, direct-API canary, pilot, budget gate, confirmatory matrix, and protected
  two-week review window are frozen in
  [`docs/12_aamas_2027_hardened_research_plan.md`](docs/12_aamas_2027_hardened_research_plan.md).
  No provider generation is authorized until E0/E1 pass.
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
| **20.0** | ContractBench FSE expansion design | `docs/14_fse_contractbench_protocol.md` | ⏸️ **SUPERSEDED FOR CURRENT CAMPAIGN** | Preserved multi-environment FSE planning reference. The narrower experiment-first AAMAS plan at Stage 22.1 now governs implementation and provider authorization. |
| **21.0** | Dynamic SCAC telemetry design and consolidation | `docs/15_dynamic_agent_telemetry_whitepaper.md` | ✅ **DONE** | Consolidated two independent drafts into one canonical, evidence-audited design with a versioned 4D state, dual-tier injection, ToolRoute/MemoryGovernor/RetryBudget scenarios, controlled comparisons, statistics, fail-closed gates, and a separate-repository implementation decision. The earlier draft remains preserved. |
| **22.1** | AAMAS experiment-first plan and scope lock | `docs/12_aamas_2027_hardened_research_plan.md` | ✅ **FROZEN** | P/R/G design with GPT-5.6 Sol, Claude Sonnet 5, and Gemini 3.8 Flash; the pilot-driven E4 freeze later fixed the full matrix at 288 trajectories and a fail-closed $30 API cap. |
| **22.2** | AAMAS E0a production-shaped vertical slice | `experiments/09_aamas_contract_bridge/`, `docs/17_aamas_e0a_report.md` | ✅ **DONE** | Bounded Debian 12 GCP worker with six-hour automatic stop; cgroup v2 memory/CPU controllers; direct-SSH imported-response execution; correctness/suitability scoring; immutable archival; measured-allocation, authentic `oom_kill`, and timeout controls. Five interface tests pass. No model API calls were made. |
| **22.3** | AAMAS E0b calibration and E1 isolated smoke | `experiments/09_aamas_contract_bridge/calibration/`, `docs/18_aamas_e0b_e1_report.md` | ✅ **DONE** | Frozen CPython 3.11.2/NumPy 2.0.2/Pandas 2.2.3 runtime, two hashed primary datasets, four opposed execution envelopes, numerical tolerance, and exact ETL oracle. All four cells passed 3/3 expected and 0/3 opposed references; numerical latency margin passed an additional 5/5 versus 0/5 check. Isolated P/R/G development fixtures all completed through the production path and remain excluded. API spend remains $0. |
| **22.4** | AAMAS hardened canary and capacity correction | `experiments/09_aamas_contract_bridge/api_canary/`, `experiments/09_aamas_contract_bridge/calibration/e0_pre_pilot_security_controls.json` | ✅ **DONE** | Generated programs execute non-root, offline, with read-only datasets, `pids.max=64`, and 1 MiB stdout/stderr caps; all controls pass. Numerical latency was recalibrated to 3.0 s (5/5 vs 0/5). Gemini 3.8 v3 cost $0.293 and exposed 4,096-token truncation; excluded. V4 at 16,384 tokens cost $0.523 and produced 8/12 suitable outcomes: both proactive numerical cells passed while reactive/generic numerical cells failed. A faster model-generated streaming parser invalidated the original ETL opposition; the redesigned task passed 5/5 vs 0/5 in both environments. V5 cost $0.235 and produced 4/6 first-pass, 5/6 final suitability, with proactive first-pass success in both environments. All canaries remain excluded. |
| **22.5** | AAMAS Gemini 3.8 non-pooled pilot | `experiments/09_aamas_contract_bridge/api_pilot/`, `docs/19_aamas_e2_e3_report.md` | ✅ **DONE** | All 24 randomized trajectories and 34 provider calls completed normally for $1.099. P: 7/8 first-pass, 8/8 final; R: 3/8, 4/8; G: 4/8, 4/8. Numerical P was 4/4 while R/G were 0/4 each. ETL implementations shifted between streaming and Pandas with the disclosed envelope. Pilot is non-pooled and excluded from confirmatory estimates. |
| **22.6** | Post-pilot cost containment | `aether-aamas-worker` | ✅ **DONE** | Dedicated GCP worker stopped after E3 completion on September 11. Restart only for the next model-free calibration or predeclared provider gate. |
| **22.7** | E4 provider access and backend freeze | `docs/21_aamas_provider_canary_report.md` | ✅ **DONE** | Exact model access and current API schemas verified. GPT-5.6 Sol was first-pass suitable at 58.5 MiB/2.085 s for $0.0664. Claude Sonnet 5 returned two complete generations for $0.0739; attempt 1 timed out and attempt 2 was kernel OOM-killed. Both are development-only, retained without replacement, and excluded. Worker stopped after completion. |
| **22.8** | E4 strategy codebook | `docs/20_aamas_strategy_codebook.md`, `src/aether_contract_bridge/strategy.py` | ✅ **FROZEN** | AST-based task-family labels plus orthogonal features and blinded adjudication rule frozen. All pilot attempts classified; no first-attempt program required adjudication. Operational suitability remains execution-derived. Ten interface tests pass. |
| **22.9** | E4 secondary instances and protocol freeze | `docs/22_aamas_e4_protocol_freeze.md`, `protocol/E4_FREEZE_VALIDATION.json` | ✅ **FROZEN** | Independent numerical and ETL instances, hashes, oracles, and four envelopes frozen. The preserved first calibration failed only the provisional 1.4 s ETL latency cell; a pre-generation change to 1.7 s produced a complete 5/5 expected vs 0/5 opposed pass. Confirmatory N=4 gives 288 trajectories and 96 per condition; provider budgets sum to $30. Eleven tests and the fail-closed E4 validator pass. |
| **22.10** | E5 Gemini 3.8 confirmatory cohort and provider gate | `docs/24_aamas_gemini_confirmatory_gate.md`, `analysis/gemini_e5_complete_audit.json` | ✅ **DONE / GATE PASSED** | All 96 effective trajectories and 158 calls completed for an estimated $4.961744. The audit reports zero integrity issues. P achieved 24/32 first-pass and 25/32 final suitability versus 5/32 and 8/32 for R and 5/32 and 10/32 for G. Numerical P was 16/16 first-pass across both instances/envelopes while R/G were 0/16; latency-tight ETL remained difficult in all conditions and is retained as a mixed result. Worker stopped; frozen Claude/GPT cohorts are approved to proceed. |
| **22.11** | E5 Claude Sonnet 5 confirmatory cohort | `docs/25_aamas_claude_confirmatory_gate.md`, `analysis/claude_e5_complete_audit.json` | ✅ **DONE / GATE PASSED** | All 96 trajectories and 173 calls completed for an estimated $1.980382. The audit reports zero integrity issues. P achieved 16/32 first-pass and 22/32 final suitability versus R at 1/32 and 9/32 and G at 2/32 and 7/32. Proactive disclosure was 8/8 first-pass in memory-tight ETL, sharply reduced OOM kills, and dominated numerical outcomes; latency-tight ETL remained difficult across conditions. Worker stopped; frozen GPT cohort is approved. |
| **22.12** | E5 GPT-5.6 Sol confirmatory cohort | `protocol/confirmatory_openai_sol.json` | 🔄 **CANARY FROZEN** | Campaign priority 3 follows independently passed Gemini and Claude gates. Before any GPT confirmatory call, the first entry of the already-frozen randomized order is locked as a one-trajectory operational canary with the parent manifest hash and a two-call cap. Its outcome cannot govern continuation; only artifact or infrastructure integrity can. |

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
- **AAMAS 2027 precursor review (2026-09-11):** Independent review identified the
  numerical-task opposed-envelope collapse, reactive-feedback confounding,
  unsupported multi-agent scope, and the need for authentic Linux enforcement.
  Those findings informed the authoritative Stage 22.1 plan; the earlier overbuilt
  four-arm specification is superseded.
- **AAMAS experiment-first revision (2026-09-11):** The authoritative plan now
  preserves reusable interfaces while moving empirical contact forward: a
  production-shaped zero-cost smoke is due Sep 13, a 12-trajectory direct-API
  canary Sep 14, and a 24-trajectory non-pooled pilot Sep 17. The primary matrix
  is P/R/G; active probing and representation ablations are gated subsets. Cloud
  adapter breadth, resource slicing, skills, a third task, second harness, and
  dynamic telemetry are deferred. Technical freeze is Sep 24 so one week remains
  for internal/IP review and one week for submission contingency.
- **AAMAS execution-plan amendment (2026-09-11; superseded at E4):** Local inspection confirmed no
  installed Docker command. E0a now selects a persistent Linux route, with GCP as
  the default, and records contract-governed child time separately from worker and
  end-to-end trajectory time. E0b measures interpreter/dependency RSS before
  selecting ETL packages or thresholds. The second instances freeze at E4, and a
  six-trajectory sanitized raw-evidence diagnostic is predeclared for E3. The
  planning set was GPT-5.6 Sol, Claude Sonnet 5, and Gemini 3.7 Flash across a
  provisional 360-trajectory matrix. E4 superseded this with Gemini 3.8 Flash and
  a 288-trajectory design. API calls fail closed at $30, plus up to $10 GCP
  credit; observed canary/pilot billing replaced token assumptions before main calls.
- **AAMAS E0a completion (2026-09-11):** The reusable contract bridge now includes
  versioned evidence/contracts, deterministic P/R/G rendering, permanent imported-
  response replay, a two-attempt decision policy, direct-SSH Linux execution,
  cgroup v2 evidence, scoring, and append-only archives. The dedicated Debian 12
  worker passed a suitable end-to-end fixture plus measurement, OOM-kill, and
  timeout controls. Two pre-execution development failures remain visibly archived
  and excluded. E0b calibration is next; API spend remains zero.
- **AAMAS E0b/E1 completion (2026-09-11):** Model-free calibration established
  clean strategy opposition in both families: numerical eager ~790.7 MiB/3.2 s
  versus bounded ~45.2 MiB/5.6 s; ETL Pandas ~270.8 MiB/1.6 s versus streaming
  ~4–6 MiB/5.4 s. The frozen memory- and latency-tight contracts reliably admit
  the intended reference and reject the opposed one. Context-isolated P/R/G smoke
  completed through the same path; all outputs are development-only.
- **AAMAS E5 Gemini-first gate (2026-09-11):** The 96-trajectory Gemini 3.8 Flash
  confirmatory cohort reached all 96 scheduled slots under the frozen $9 cap.
  Slots 1–64 completed; every provider request beginning at slot 65 failed with
  HTTP 429, leaving 32 infrastructure-failed slots. The 103 completed calls cost
  an estimated $3.066. The ledger also retains 32 un-settled reservations totaling
  $3.936; these are not treated as billed calls. The worker was stopped. The 429
  slots are infrastructure exclusions, not unsuitable model outcomes, and remain
  permanently archived. Claude and GPT will not start until Gemini is completed
  under an outcome-neutral resume rule and passes the conference-calibrated audit.
- **AAMAS E5 fail-fast amendment (2026-09-11):** After the 429 diagnosis and
  before any resume call, provider HTTP failures were changed to release their
  local reservation, stop the runner immediately, and force a nonzero result
  until every scheduled trajectory is complete. The exact outcome-neutral resume
  rule is frozen in `docs/23_aamas_e5_infrastructure_interruption.md`.
- **AAMAS E5 resume prepared (2026-09-11):** A machine-derived manifest freezes
  only slots 65–96, verifies that each has zero generated attempts and an HTTP 429
  failure, links every replacement to its original trajectory, allows at most 64
  calls, and limits additional estimated spend to $5.934170. No resume call has
  been issued; quota/billing access must first be verified.
- **Gemini quota diagnosis (2026-09-11):** Read-only inspection of Google AI
  Studio confirmed that project `gst-ai` remains on the Free tier and its billing
  page reports that prepayment is required and no prepayment method is configured.
  The frozen resume remains unstarted. Configure prepaid billing before resuming;
  the experiment must not interpret the HTTP 429 interruption as a model outcome.
- **AAMAS E5 partial evidence audit (2026-09-11):** The reusable cohort auditor
  verified all 64 completed Gemini trajectories with zero prompt, manifest,
  artifact, retry, model, or scoring inconsistencies. It identifies exactly 32
  incomplete slots, all pre-generation HTTP 429 failures. Diagnostic counts are
  P 16/22 first-pass and 17/22 final, R 4/22 and 7/22, and G 5/20 and 8/20;
  these are explicitly incomplete and not confirmatory estimates.
- **AAMAS confirmatory analysis implementation (2026-09-11):**
  `benchmarks/analyze_aamas_confirmatory.py` now implements the analysis frozen
  before provider calls: equal-stratum first-pass risk differences, 100,000
  within-stratum label permutations, Holm correction, Wilson intervals, 20,000
  stratified bootstrap resamples for continuous outcomes, and stratified
  behavioral/failure summaries. It refuses to run unless three complete,
  integrity-passing 96-trajectory audits produce the exact balanced 288-run
  matrix. The cohort auditor now emits the compact execution, token, cost, and
  strategy evidence required by that analysis; all 13 unit tests pass.
- **AAMAS Gemini resume canary (2026-09-11):** The user corrected the Gemini
  account spending cap. Before releasing all 32 frozen replacements, an immutable
  one-trajectory operational canary selects the first entry in the existing
  resume order (original slot 65), retains the same model, prompt, environment,
  archive namespace, and budget ledger, and caps execution at two provider calls.
  This is an infrastructure gate only; the selected trajectory remains part of
  the confirmatory cohort and its outcome cannot change whether the other 31 run.
- **AAMAS Gemini cohort completion (2026-09-12):** All 32 outcome-neutral
  replacements completed after the one-slot infrastructure gate, producing a
  complete 96-trajectory effective cohort. The fail-closed audit passes with zero
  integrity issues. P is 24/32 first-pass and 25/32 final versus R at 5/32 and
  8/32 and G at 5/32 and 10/32. The estimated API cost is $4.961744 across 158
  calls. The dedicated worker is stopped. The frozen Claude and GPT cohorts are
  authorized to begin only under their existing manifests.
- **AAMAS Claude cohort completion (2026-09-12):** All 96 trajectories completed
  and passed the fail-closed audit with zero integrity issues. P achieved 16/32
  first-pass and 22/32 final suitability, versus R at 1/32 and 9/32 and G at
  2/32 and 7/32. The cohort used 173 calls and an estimated $1.980382, below the
  frozen $8 cap. The worker is stopped and the GPT cohort is cleared to proceed.
