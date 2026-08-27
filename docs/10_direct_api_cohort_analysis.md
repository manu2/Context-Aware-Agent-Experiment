# Direct-API Cohort Analysis (No Manuscript Changes)

**Status:** Post-run analysis of protocol v1.2 artifacts. This note does not modify
`paper_draft.md` and does not pool these observations with historical cohorts.

## Included direct-API cohorts

| Model | Completed clean pairs | Blind correct / within 128 MB | Telemetry correct / within 128 MB | RSS direction among executable pairs |
|---|---:|---|---|---|
| Claude Opus 5 | 5 (`rep02`–`rep06`) | 4/5, 0/5 | 5/5, 5/5 | lower in 4/4 |
| GPT-5.6-Sol | 4 (`rep01`–`rep04`) | 4/4, 3/4 | 4/4, 4/4 | lower in 3/4; higher in 1/4 |
| Gemini 3.7 Flash | 4 (`rep01`–`rep04`) | 4/4, 0/4 | 4/4, 2/4 | lower in 4/4 |

The excluded `opus_rep01` pair is not included. The project-owner-confirmed prior
GPT direct pair is not included until its artifact location is indexed in the
repository.

## Quantitative summary

| Model | Blind mean MaxRSS | Telemetry mean MaxRSS | Mean paired RSS change | Blind mean wall time | Telemetry mean wall time |
|---|---:|---:|---:|---:|---:|
| Claude Opus 5 | 256.48 MB* | 107.82 MB | -148.10 MB* | 0.9109 s* | 0.3612 s |
| GPT-5.6-Sol | 118.05 MB | 66.92 MB | -51.14 MB | 0.5477 s | 0.3400 s |
| Gemini 3.7 Flash | 473.73 MB | 156.40 MB | -317.32 MB | 1.1091 s | 0.3621 s |

`*` Claude blind means and paired deltas exclude `opus_rep04_A`, which failed under
the pinned Python 3.9.6 interpreter because the generated script used Python 3.10
union-type syntax. It remains a blind first-pass failure in the success-rate table.

## Findings supported by this cohort

1. **Fresh Claude replication is particularly strong.** Every telemetry script was
   correct and below the observed 128 MB threshold; no blind script achieved both
   correctness and that threshold. The four executable pairs all reduced RSS.
2. **The response is model-dependent, not universal.** GPT telemetry reduced RSS in
   three pairs but increased it in `rep04` (65.70 to 87.64 MB). Gemini telemetry
   reduced RSS in all four pairs but met the 128 MB threshold in only two.
3. **Threshold crossing is secondary to paired adaptation.** GPT blind outputs
   sometimes happened to fit 128 MB, yet telemetry still commonly selected lower-RSS
   variants. This supports the constraint-sensitivity framing in
   `docs/09_constraint_sensitivity_framing_notes.md`.
4. **No cgroup-survivability claim follows from this cohort.** These are macOS
   `RUSAGE_CHILDREN` MaxRSS classifications, not runs under an enforced memory cap.

## Relationship to the current manuscript

The historical Table 1 values in `paper_draft.md` are not invalidated; the fresh
Claude direct cohort reproduces their qualitative pattern. They must remain a
separate historical cohort because their generation/provenance pipeline predates
protocol v1.2. The manuscript's historical GPT result is likewise compatible with
the fresh data's mixed GPT behavior.

Before revising the manuscript:

1. Add a separate direct-API replication table; do not add its rows to the current
   historical N=5 table or recompute one combined p-value.
2. Report all mixed outcomes, including Claude `rep04_A`, GPT `rep04`, and Gemini's
   2/4 direct observed-budget compliance.
3. Update the main framing to paired constraint sensitivity and observed resource
   adaptation; present budget compliance as a secondary outcome.
4. Clearly separate fresh observed-RSS results from historical enforced-cgroup
   results and reconcile the historical Gemini Phase 2 JSON/report discrepancy
   before quoting an aggregate from it.
5. Index the owner-confirmed earlier GPT direct pair before including it in any
   numeric fresh-cohort count.
