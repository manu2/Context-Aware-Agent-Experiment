# arXiv Preprint v7: Targeted Revision Plan

**Status:** Complete manuscript-only revision, 2026-09-04.  
**Objective:** Produce a crisp, evidence-led preprint revision that makes the
completed single-turn study fully transparent, preserves its central finding, and
distinguishes that finding from the broader research agenda. No new model calls or
execution trials are authorized by this plan.

## Revision principle

The paper's central result remains direct: supplying a factual RAM/time operating
contract changed the implementation distributions selected by the evaluated model
configurations and materially improved observed resource-time outcomes in the
numerical code-generation study. The revision strengthens that result by making
the experimental unit, measurement definitions, artifact trail, and evidence
boundary explicit. It does not recast the result as tentative or retract the
broader substrate-awareness agenda.

## Frozen evidence boundary

- **Evaluated decision:** one-shot selection of an executable numerical program.
- **Primary intervention:** task-only prompt versus the same task plus a 128 MB
  RAM and 10.0 s wall-time contract.
- **Primary evidence:** fresh direct-API condition cohorts for Claude Opus 5,
  GPT-5.6-Sol, and Gemini 3.7 Flash; raw sources and profiles are archived.
- **96 MB extension:** separately generated condition-level aware cohorts, not
  matched triples and not a cgroup-survival experiment.
- **Not measured in this preprint:** multi-turn repair costs, token savings,
  live agent-harness outcomes, cloud bills, runtime-version disclosure effects,
  or other contract dimensions.

## Accepted revision actions

| ID | Change | Evidence source | Destination |
|---|---|---|---|
| R1 | Define the experiment as controlled single-turn implementation selection while retaining the broader agent-planning proposition. | Prompt and execution records | Abstract; §§1–3 |
| R2 | Replace statistical-pair terminology with condition-cohort language. A/D indices remain traceability identifiers; they do not make provider generations statistically matched. | `RUN_MANIFEST.json`; protocol | §§3–4; Table 1; Fig. 1 |
| R3 | Replace Figure 1's connected paired-ratio graphic with an accessible condition-level MaxRSS plot: independent raw observations and means, normalized within model to the task-only mean (100%), a model-specific 128 MiB threshold, and no implied matching. Keep native MiB values in Table 1 and Appendix A. | Per-trial metadata | Figure 1 and caption |
| R4 | Give Table 1 a caption and cohort-level columns; harmonize threshold terminology with Table 2. | Per-trial metadata | Table 1 |
| R5 | Publish the exact prompt text, model IDs, sampling policy, output limits, no-user-system-prompt rule, timestamps, environment, dataset hash, and archive link in a compact reproducibility record. | Manifest, conditions, metadata | §3 / Appendix B |
| R6 | State the numerical rule exactly: finite `TOTAL_DIST` with relative error `< 1e-4` against the archived reference. | `run_replication.py` | §3.2 |
| R7 | State the macOS MaxRSS conversion and scoring semantics exactly. Prompt strings retain `MB`; observed values are reported in MiB (`bytes / 2^20`). The archived 128 MB scorer uses `<128 MiB`; the descriptive 96 MB table uses `<=96 MiB`. | Runner, environment record, and 96 MB report | §3.2; table headings |
| R8 | Define response-invalid handling: empty or truncated provider output is retained, classified, and replaced only under the documented same-prompt rule. | 96 MB manifest | §3.2 / Appendix B |
| R9 | Make the 128→96 MiB time increase explicit while retaining the blind-reference improvement. | Table 2 | §4.3 |
| R10 | Label the Python 3.9 incident as an illustrative observed compatibility case motivating a future version-contract test. | `opus_rep04_A` artifact | §6 |
| R11 | Add compact descriptive spread summaries from existing artifacts. Retain the source-linked audit rather than force a frequency matrix whose coarse token features do not faithfully represent the heterogeneous algorithmic adaptations. Do not add invalid paired tests. | Code audit and profiles | Appendix B |
| R12 | Add relevant efficiency and execution-feedback literature; retain cloud impact as a provisioning opportunity, not a measured billing claim. | Scholarly sources; measured profiles | §§5–6 |
| R13 | Replace the future-public-release wording with the cleared GitHub repository URL and a formal artifact reference. | Public repository release | §7; References |
| R14 | Point Appendix B to the machine-readable per-run audit (trial ID, outcome, profile, and source features) rather than expand the preprint into a 45-row appendix table. | `fresh_code_transformation_audit.json` | Appendix B |
| R15 | Remove introductory repetition; name single-turn code generation as the implementation-selection primitive and the task as an inspectable deterministic micro-benchmark. Make the related-work antecedent explicit; improve review-PDF tables and widow/orphan handling. | Existing manuscript and renderer | §§1–3, §5; review PDF |

## Deliberately deferred to the FSE-scale expansion

- Multi-task and multi-contract benchmark matrix.
- Linux cgroup admission / kernel event measurements.
- Reactive repair, token, and trajectory comparisons.
- Runtime-version, accelerator, tool, permission, quota, and cost treatments.
- Measured cloud billing and provisioning-tier experiments.

These are high-value extensions, not corrections to the completed proof of
concept. They remain planned in the ContractBench/FSE protocol.

## Figure 1 decision

The prior graphic indexed each disclosed result to an identically numbered blind
generation. That visualization makes independent generations look matched. The
replacement shows the two condition cohorts directly while normalizing each panel
to its own task-only mean (100%):

- one panel per model configuration on a common percentage scale, so it shows each
  model's within-configuration shift rather than a capability leaderboard;
- task-only and contract-disclosed raw points with deterministic horizontal jitter;
- an explicit mean marker and a model-specific 128 MiB observed-threshold line;
- text labels and marker shapes in addition to colour; and
- a visible annotation for Claude's retained runtime failure, whose missing MaxRSS
  is not plotted as a numerical point.

This presents the observed evidence more honestly and more clearly: readers can
inspect the full within-model distribution without interpreting arbitrary A/D
indices as matched pairs or comparing model panels as a capability leaderboard.
Table 1 and Appendix Figure A1 retain all absolute MiB values.

## Completion criteria

1. The canonical `paper_draft.md` v7 revision preserves every empirical number
   unless a units label or threshold operator is corrected to match the archived
   scorer; the prior v6 source remains archived under `paper/archive/manuscripts/`.
2. Figure source, figure files, manuscript references, and verification checks
   agree.
3. The rendered v7 PDF has no overlapping labels, unlabeled colour semantics,
   clipped tables, orphaned headings, or broken repository links.
4. The evidence-package verifier and manuscript consistency audit pass.
5. The v7 review PDF passes visual and numerical review before any submission or
   public-release action.

## Completion record

- `paper_draft.md`, figures, README, and evidence verifier now use the same
  task-only/contract-disclosed condition terminology and native MiB measurement
  convention.
- Figure 1 is a within-model normalized condition-cohort display; Table 1 and
  Appendix Figure A1 preserve the absolute outcomes.
- The review PDF renderer embeds 2400-pixel figure previews. The source figures
  remain vector PDFs for the eventual TeX/arXiv package.
- `benchmarks/verify_fresh_evidence_package.py --manuscript paper_draft.md` and
  `git diff --check` pass on the completed revision.
- The final polish pass removes redundant framing, makes the experimental primitive
  explicit, and upgrades review-PDF table/header and page-break hygiene without
  changing any evidence or result.
