# Direct-API Cohort Analysis (No Manuscript Changes)

**Status:** Complete post-run analysis of protocol v1.2 artifacts (2026-08-27).
This note does not modify `paper_draft.md` and does not pool these observations
with historical cohorts.

## Included direct-API cohorts

| Model | Completed clean pairs | Blind correct / within 128 MB | Telemetry correct / within 128 MB | RSS direction among executable pairs |
|---|---:|---|---|---|
| Claude Opus 5 | 5 (`rep02`–`rep06`) | 4/5, 0/5 | 5/5, 5/5 | lower in 4/4 |
| GPT-5.6-Sol | 5 (`rep01`–`rep05`) | 5/5, 4/5 | 5/5, 5/5 | lower in 4/5; higher in 1/5 |
| Gemini 3.7 Flash | 5 (`rep01`–`rep05`) | 5/5, 0/5 | 5/5, 2/5 | lower in 5/5 |

The excluded `opus_rep01` pair is not included. The project-owner-confirmed prior
GPT direct pair is not included until its artifact location is indexed in the
repository.

## Quantitative summary

| Model | Blind mean MaxRSS | Telemetry mean MaxRSS | Mean paired RSS change | Blind mean wall time | Telemetry mean wall time |
|---|---:|---:|---:|---:|---:|
| Claude Opus 5 | 256.48 MB* | 107.82 MB | -148.10 MB* | 0.9109 s* | 0.3612 s |
| GPT-5.6-Sol | 118.63 MB | 64.61 MB | -54.02 MB | 0.5507 s | 0.3282 s |
| Gemini 3.7 Flash | 452.36 MB | 158.16 MB | -294.20 MB | 1.0994 s | 0.3561 s |

`*` Claude blind means and paired deltas exclude `opus_rep04_A`, which failed under
the pinned Python 3.9.6 interpreter because the generated script used Python 3.10
union-type syntax. It remains a blind first-pass failure in the success-rate table.

## Findings supported by this cohort

1. **Fresh Claude replication is particularly strong.** Every telemetry script was
   correct and below the observed 128 MB threshold; no blind script achieved both
   correctness and that threshold. The four executable pairs all reduced RSS.
2. **The response is model-dependent, not universal.** GPT telemetry reduced RSS in
   four pairs but increased it in `rep04` (65.70 to 87.64 MB). Gemini telemetry
   reduced RSS in all five pairs but met the 128 MB threshold in only two.
3. **Threshold crossing is secondary to paired adaptation.** GPT blind outputs
   sometimes happened to fit 128 MB, yet telemetry still commonly selected lower-RSS
   variants. This supports the constraint-sensitivity framing in
   `docs/09_constraint_sensitivity_framing_notes.md`.
4. **No cgroup-survivability claim follows from this cohort.** These are macOS
   `RUSAGE_CHILDREN` MaxRSS classifications, not runs under an enforced memory cap.
5. **The fresh effect is not uniformly a switch from a naive to a blocked
   algorithm.** Several blind outputs already use blocking and symmetry (all five
   fresh GPT blind outputs and four executable fresh Claude blind outputs). Within
   this cohort, telemetry commonly changes block size, precision, buffering, or
   the extent of the matrix traversed. The manuscript must therefore describe a
   change in *resource-relevant implementation choices*, not claim that every
   blind output used a full eager matrix or that every telemetry output discovered
   blocking for the first time.

## Complete row-level record

All 32 predeclared manifest IDs now have an archived `metadata.json`; the retained
duplicate `opus_rep01_A/D` record is excluded from
analysis; and `opus_rep04_A` is an executable first-pass failure rather than a
missing value. The included rows below are read directly from each trial's
`metadata.json`.

| Model | Pair | Blind MaxRSS / correct / <=128 MB | Telemetry MaxRSS / correct / <=128 MB |
|---|---|---|---|
| Claude Opus 5 | `rep02` | 206.02 / yes / no | 107.48 / yes / yes |
| Claude Opus 5 | `rep03` | 168.59 / yes / no | 102.80 / yes / yes |
| Claude Opus 5 | `rep04` | 19.95 / **no** / no | 105.56 / yes / yes |
| Claude Opus 5 | `rep05` | 345.33 / yes / no | 111.86 / yes / yes |
| Claude Opus 5 | `rep06` | 305.97 / yes / no | 111.38 / yes / yes |
| GPT-5.6-Sol | `rep01` | 113.06 / yes / yes | 65.83 / yes / yes |
| GPT-5.6-Sol | `rep02` | 179.92 / yes / no | 60.00 / yes / yes |
| GPT-5.6-Sol | `rep03` | 113.53 / yes / yes | 54.20 / yes / yes |
| GPT-5.6-Sol | `rep04` | 65.70 / yes / yes | 87.64 / yes / yes |
| GPT-5.6-Sol | `rep05` | 120.92 / yes / yes | 55.38 / yes / yes |
| Gemini 3.7 Flash | `rep01` | 306.38 / yes / no | 124.91 / yes / yes |
| Gemini 3.7 Flash | `rep02` | 367.06 / yes / no | 170.31 / yes / no |
| Gemini 3.7 Flash | `rep03` | 671.52 / yes / no | 216.05 / yes / no |
| Gemini 3.7 Flash | `rep04` | 549.95 / yes / no | 114.34 / yes / yes |
| Gemini 3.7 Flash | `rep05` | 366.89 / yes / no | 165.19 / yes / no |

`<=128 MB` means a correct, exit-zero run with observed MaxRSS strictly below
128 MB. It is not an assertion that an OS resource controller killed or admitted
the process at that boundary. The `opus_rep04_A` number must not enter the Claude
blind mean because the script did not execute; it is retained in the correctness
denominator and documented as a first-pass failure.

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
   2/5 direct observed-budget compliance.
3. Update the main framing to paired constraint sensitivity and observed resource
   adaptation; present budget compliance as a secondary outcome.
4. Clearly separate fresh observed-RSS results from historical enforced-cgroup
   results and reconcile the historical Gemini Phase 2 JSON/report discrepancy
   before quoting an aggregate from it.
5. Index the owner-confirmed earlier GPT direct pair before including it in any
   numeric fresh-cohort count.

## Proposed manuscript revision plan (do not apply yet)

1. Keep current Table 1 explicitly titled **historical canonical post-hoc
   profiling**. It remains numerically auditable, but it is a separate cohort.
2. Add a new **direct-API replication** table containing all 15 included pairs and
   an explicit failure marker for `opus_rep04_A`. Do not pool p-values, means, or
   compliance fractions across the two provenance pipelines.
3. Make the headline result: *constraint disclosure changed paired generated
   resource-relevant implementation choices and usually lowered observed MaxRSS;
   the strength and threshold compliance varied by model.* The fresh cohort independently reproduces a strong
   Claude result (0/5 blind versus 5/5 telemetry correct-and-under-threshold), gives
   mixed-but-favorable GPT evidence (4/5 lower RSS; 5/5 telemetry threshold), and
   directional but incomplete Gemini evidence (5/5 lower RSS; 2/5 telemetry
   threshold).
4. State the threshold interpretation carefully: a blind GPT script fitting at
   128 MB is not evidence it was conditioned on a limit; it is a successful output
   under this one observed boundary. The experiment supports a paired behavior
   change, not an untested claim about a hypothetical 96 MB boundary.
5. In Methods and Limitations, name macOS `RUSAGE_CHILDREN`, the frozen Python and
   NumPy versions, prompt/dataset hashes, provider/model IDs, and the atomic
   write-once reservation. Limit "survives a 128 MB cgroup" language to artifacts
   actually run under an enforced cgroup.
6. Correct bibliographic metadata and reconcile the historical Phase 2
   `results.json`/prose conflict before submission. These are manuscript blockers
   independent of the completed direct-API trial count.
7. Amend the historical measurement description: its `profile_canonical_maxrss.py`
   treats any emitted `TOTAL_DIST` as a successful execution and does not compare it
   to the ground truth. The archived
   [`historical exact-output verification`](../experiments/06_replication/audit/historical_exact_output_verification_2026-08-27.json)
   using the v1.2 validator found all 20 historical scripts correct, but a future
   revision should either make the canonical profiler apply the same
   correctness check. Treat its one-shot MaxRSS numbers as archived measurement
   snapshots, not an enforced-cap result.
