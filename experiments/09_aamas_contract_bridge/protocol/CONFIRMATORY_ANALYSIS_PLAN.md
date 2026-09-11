# Confirmatory analysis plan v1.0

**Frozen before confirmatory provider calls:** 2026-09-11
**Pilot and all canaries:** development-only; never pooled with confirmatory data

## Design and experimental unit

The experimental unit is one independently generated trajectory. Index order is
randomized bookkeeping, not statistical pairing. The frozen matrix contains
three provider-configured models, two task families, two independently generated
instances per family, two opposed execution environments, three information
conditions, and four repetitions per cell:

`3 x 2 x 2 x 2 x 3 x 4 = 288 trajectories`

Each trajectory permits at most two provider calls: an initial implementation and
one repair after authentic execution evidence. Every issued provider call and
every created trajectory remains in the attempted-run ledger. A provider error,
unparseable response, incorrect program, timeout, OOM kill, or missing execution
is scored unsuitable; there are no outcome-based replacements.

## Conditions

- **P — proactive contract:** exact compiled target contract is visible before
  initial implementation selection.
- **R — reactive discovery:** task-only initial state; authentic execution
  observation is supplied only after an unsuitable first attempt.
- **G — generic efficiency:** balanced memory/time efficiency guidance without
  target values; authentic observation follows an unsuitable first attempt.

## Outcomes

The two co-primary estimands are the stratified risk differences in verified
first-pass suitability for **P minus R** and **P minus G**. Suitability requires a
correct oracle result, no timeout or OOM kill, and execution within both memory
and wall-time bounds.

Secondary outcomes are final suitability within two attempts; provider calls and
tokens per successful trajectory; failed executions before success; end-to-end
recovery latency; program time; memory peak and exceedance; and the frozen static
strategy labels/features. Static strategy classification is behavioral evidence
only and never overrides execution-derived suitability.

## Estimation and inference

- Report raw counts, denominators, risk differences, and 95% Wilson intervals for
  each condition overall and by model, task family, instance, and environment.
- For each co-primary contrast, use an equal-stratum-weighted difference in
  first-pass suitability across model x family x instance x environment strata.
- Obtain a two-sided randomization p-value from 100,000 within-stratum condition-
  label permutations with seed `20260924`.
- Control the two co-primary p-values with Holm's procedure at family-wise
  alpha 0.05. Emphasize effect sizes and intervals, not threshold crossing alone.
- Use a stratified nonparametric bootstrap with 20,000 resamples and seed
  `20260925` for secondary continuous-outcome intervals. Failed trajectories do
  not receive invented memory/time values; failure-type counts accompany the
  available continuous distributions.
- Condition-by-model, task-family, and environment interactions are exploratory
  and reported without universal model-ranking claims.

## Sample size and cost lock

Four repetitions yield 96 trajectories per condition and retain replication in
every frozen stratum. A simple two-proportion planning approximation has about
93% power for a 25-percentage-point difference near a 50% control rate at a
conservative two-sided 0.025 threshold; the confirmatory test remains the
predeclared stratified randomization analysis.

Observed cost per completed provider call was $0.03233 in the 34-call Gemini
pilot, $0.03697 in the two-call Claude canary, and $0.06637 in the one-call OpenAI
canary. Applying those rates to the hard maximum of 192 calls per provider gives
$26.05; a 15% reserve gives $29.96. Provider caps are therefore frozen at $9
(Gemini), $8 (Claude), and $13 (OpenAI), totaling $30. The campaign stops if a
cap is reached and reports all completed/failed attempts; it does not silently
reduce conditions or models.

## Reporting commitments

All four instance/envelope cells, all three conditions, and all three models are
reported. Pilot-informed task calibration, failed calibration attempt, provider
canaries, exclusions, manifests, prompts, raw responses, extracted programs,
execution evidence, code hashes, and analysis code remain public as separate
development or confirmatory artifacts. No prompt, threshold, taxonomy, oracle,
stopping rule, or primary contrast changes after the first confirmatory call.
