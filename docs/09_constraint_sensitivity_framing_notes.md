# Constraint-Sensitivity Framing Notes

**Status:** Working notes for a later manuscript revision. This document does not
change `paper_draft.md` and does not add a new experimental claim.

## Core interpretation

The empirical question is not whether a blind-generated program is universally
"bad," nor whether it happens to pass one chosen memory threshold. The question is
whether giving a model an explicit operating boundary changes the program it
generates and its observed resource use.

A blind program can happen to fit a 128 MB reference budget without knowing that
such a budget exists. That outcome is not evidence that the model deliberately
calibrated its algorithm to the deployment substrate. Conversely, any sufficiently
large memory budget can make otherwise resource-expensive programs appear
successful. The evidence of interest is the paired behavioral change after the
boundary is disclosed.

## The 96 MB example: correct use and limits

The direct-API GPT blind pilot observed 113.06 MB MaxRSS, while its telemetry
counterpart observed 65.83 MB. Therefore the blind program would be classified as
over a *96 MB observed-RSS reference threshold*, while the telemetry program would
be under it. This is a useful illustration of why accidental success at 128 MB and
constraint-aware adaptation are different concepts.

It is **not** evidence that the blind program would be killed under a real 96 MB
container cap, or that the model would generate the same program if prompted with
96 MB. Neither counterfactual was tested. The present study should not introduce a
96 MB prompt condition merely to make this rhetorical point.

## Suggested manuscript framing

> A blind-generation success at a particular budget should not be interpreted as
> constraint-aware behavior. A program may happen to fall below a 128 MB reference
> threshold, but it is not calibrated to that boundary and offers no basis to expect
> suitability under a tighter or otherwise different deployment limit. Substrate
> disclosure instead gives the model information with which to adapt implementation
> choices to the stated operating boundary.

Use the following hierarchy when revising the manuscript:

1. **Primary outcome:** paired change in generated implementation choices and
   observed resource use after explicit boundary disclosure.
2. **Secondary outcome:** whether the observed process MaxRSS crosses the stated
   128 MB reference threshold.
3. **Do not claim:** cgroup/container survival, a 96 MB counterfactual outcome, or
   CPU-quota adaptation. The current direct-API pilot observes MaxRSS and wall time;
   it does not enforce a memory cap or CPU quota.

This framing accommodates model-specific outcomes. For example, the GPT blind
pilot already met the 128 MB observed-RSS threshold, yet its telemetry counterpart
still used substantially less memory. That is evidence of a paired resource-use
change, not a contradiction.

## Repository evidence to cite later

- Historical primary paired cohort: five A/D pairs each for Claude Opus and GPT in
  [`docs/06_statistical_paired_report.md`](06_statistical_paired_report.md) and
  [`experiments/05_paired_statistical_trials/canonical_paired_results.json`](../experiments/05_paired_statistical_trials/canonical_paired_results.json).
- Fresh direct-API pilot: one clean A/D pair each for Claude Opus, GPT, and Gemini
  in [`docs/07_direct_api_pilot_report.md`](07_direct_api_pilot_report.md).
- GPT direct-pilot source records:
  [`A metadata`](../experiments/06_replication/raw/gpt-5.6-sol/gpt_rep01_A/metadata.json)
  and [`D metadata`](../experiments/06_replication/raw/gpt-5.6-sol/gpt_rep01_D/metadata.json).
- Frozen task, prompt hashes, and direct API configuration:
  [`experiments/06_replication/RUN_MANIFEST.json`](../experiments/06_replication/RUN_MANIFEST.json)
  and [`run_replication.py`](../experiments/06_replication/run_replication.py).

No external scholarly citation is required for the 96 MB illustration: it is a
bounded interpretation of the recorded measurements, not a general scientific
claim.
