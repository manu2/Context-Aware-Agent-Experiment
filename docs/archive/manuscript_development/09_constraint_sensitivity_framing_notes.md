# Constraint-Sensitivity Framing Notes

**Status:** Working notes for a later manuscript revision. This document does not
change `paper_draft.md`; it reflects the completed, separately labelled 96 MB
condition-level sweep.

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

## The 96 MB extension: correct use and limits

The direct-API GPT blind pilot observed 113.06 MB MaxRSS, while its 128 MB-aware
counterpart observed 65.83 MB. This illustrates why accidental success at one
reference boundary and constraint-aware adaptation are different concepts.

The project subsequently added a separately labelled `96 MB + 10 s` local sweep:
five new aware generations each for GPT, Claude, and Gemini, with existing blind
and 128 MB-aware cohorts used only as condition-level references. Correct and
observed-`<=96 MB` outcomes were GPT 5/5, Claude 4/5, and Gemini 3/5. These are
not matched three-condition trajectories and do not establish a cgroup-survival
counterfactual for any blind program. See
[`LOCAL_SWEEP_REPORT.md`](../experiments/08_96mb_cgroup_pilot/LOCAL_SWEEP_REPORT.md).

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

## Software-substrate illustration: Python runtime compatibility

The retained `opus_rep04_A` blind response used a Python 3.10-style union
annotation (`int | None`) and failed when that annotation was evaluated under the
pinned Python 3.9.6 runtime. This is **not** an additional treatment result: the
study did not disclose a Python version in a paired condition, so it cannot show
that version disclosure would have prevented the failure.

It is nevertheless a useful concrete illustration of the broader principle. The
runtime version is execution context just as a memory limit is execution context;
functionally plausible source can be unsuitable for the actual environment. In the
paper, describe it as an observed compatibility incident that motivates a future
controlled *runtime-version-aware generation* study, never as evidence of a tested
causal effect.

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
