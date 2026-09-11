# AAMAS E4 confirmatory protocol freeze

**Date:** 2026-09-11
**Status:** passed; confirmatory generation authorized by the frozen manifests

## Frozen matrix

The confirmatory campaign contains 288 independently generated trajectories:
three provider-configured models, two task families, two deterministic instances
per family, two opposed environments, three information conditions, and four
repetitions per cell. Each model contributes 96 trajectories and at most 192
provider calls. Conditions are independently generated and are not statistical
pairs.

The configurations are Gemini 3.8 Flash, GPT-5.6 Sol, and Claude Sonnet 5, all at
explicit medium effort/thinking. The provider-specific manifests cap aggregate
API spend at $30: $9, $13, and $8 respectively.

The campaign executes Gemini 3.8 Flash first as the lowest-cost setup gate. After
the complete Gemini cohort, the campaign pauses for a conference-calibrated review
of methodology, outcomes, completeness, and artifact integrity. GPT and Claude
begin only if that review supports proceeding. This ordering does not alter sample
inclusion, stopping rules, or the analysis plan.

## E5 infrastructure interruption

The first Gemini execution reached all 96 scheduled slots, but only slots 1–64
completed. Every request beginning at slot 65 returned HTTP 429; the remaining 32
slots are therefore infrastructure failures, not generated-program outcomes. All
records are preserved. The 103 completed provider calls have estimated settled
cost $3.066; 32 failed-call reservations totaling $3.936 remain visible in the
ledger but are not interpreted as billed usage. The GCP worker was stopped.

No later provider begins until the active Gemini quota/billing state is resolved,
the missing slots are completed under a documented outcome-neutral resume rule,
and the full cohort passes the predeclared review gate.

## Second-instance calibration

The secondary numerical instance uses an independently seeded 8000 x 1024
float32 array. The secondary ETL instance uses a separate deterministic
three-million-row CSV and different filter/weight constants. Dataset byte sizes,
SHA-256 hashes, prompts, and oracles are frozen in their task specifications.

The first calibration attempt passed three envelopes but rejected both ETL
references at the provisional 1.4-second secondary latency limit. That complete
failed record is preserved. Before model exposure, only this threshold was moved
to 1.7 seconds: five DataFrame executions then passed and five streaming
executions failed. A complete rerun passed all four cells 5/5 for the expected
strategy and 0/5 for its opposed reference.

## Analysis and integrity controls

The co-primary contrasts are proactive versus reactive and proactive versus
generic guidance for verified first-pass suitability. The analysis plan freezes
the stratified permutation test, Holm correction, interval procedures, failure
handling, seeds, and reporting commitments. Every issued call and trajectory
remains in the ledger; there are no outcome-based replacements.

The strategy codebook is frozen as secondary behavioral evidence. Confirmatory
attempts archive their protocol snapshot, generated source, provider response,
static strategy record, execution observation, score, and hashes. Operational
suitability remains determined only by correctness and Linux cgroup/time evidence.

`benchmarks/validate_aamas_e4_freeze.py` verifies the 96 balanced trajectories
per provider, four repetitions in every cell, pristine confirmatory directories,
secondary calibration, task schemas and hashes, $30 aggregate cap, analysis and
codebook presence, and SHA-256 hashes of all execution-critical sources.
