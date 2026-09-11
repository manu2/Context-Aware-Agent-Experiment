# AAMAS E5 Gemini 3.8 Flash Confirmatory Gate

**Date:** 2026-09-12  
**Status:** Complete; integrity gate passed; remaining provider cohorts approved  
**Model:** `gemini-3.8-flash`  
**Evidence:** 96 confirmatory trajectories, 158 provider calls, two task families,
two independently generated instances per family, two opposed execution
envelopes, and three planning conditions

## Decision

Proceed with the frozen Claude Sonnet 5 and GPT-5.6 Sol cohorts without changing
the task specifications, execution envelopes, prompts, retry policy, scoring,
strategy codebook, or confirmatory analysis plan.

The Gemini cohort passes the conference-oriented gate. All 96 scheduled slots
have complete effective trajectories and the fail-closed audit reports zero
prompt, manifest, model, replacement, retry, artifact, or scoring inconsistencies.
The completed results show a large first-pass advantage for proactive contract
availability and a meaningful boundary condition in latency-tight ETL. Both are
retained as scientific results.

## Cohort-level outcomes

| Condition | First-pass suitable | Final suitable | Provider calls |
|---|---:|---:|---:|
| Proactive exact contract (P) | 24/32 (75.0%) | 25/32 (78.1%) | 40 |
| Reactive execution observation (R) | 5/32 (15.6%) | 8/32 (25.0%) | 59 |
| Generic efficiency guidance (G) | 5/32 (15.6%) | 10/32 (31.3%) | 59 |

The descriptive first-pass risk difference is **+59.4 percentage points** for P
against either R or G. Formal multi-model inference remains intentionally locked
until all three 96-trajectory cohorts are complete.

## Stratified outcomes

| Task family | Environment | P first/final | R first/final | G first/final |
|---|---|---:|---:|---:|
| Numerical | Memory-tight | 8/8, 8/8 | 0/8, 0/8 | 0/8, 0/8 |
| Numerical | Latency-tight | 8/8, 8/8 | 0/8, 0/8 | 0/8, 0/8 |
| ETL | Memory-tight | 8/8, 8/8 | 5/8, 7/8 | 4/8, 7/8 |
| ETL | Latency-tight | 0/8, 1/8 | 0/8, 1/8 | 1/8, 3/8 |

The numerical result is uniform across both independent datasets and both
opposed envelopes: proactive disclosure is 16/16 first-pass suitable while R
and G are each 0/16. Memory-tight ETL also favors proactive disclosure, although
the comparison conditions already discover viable streaming strategies often.

Latency-tight ETL is the important mixed result. Gemini frequently generated
chunked or streaming implementations that were memory-efficient but did not
complete and print the exact answer within 1.7 seconds. Proactive disclosure was
therefore not sufficient for this cell, and generic guidance recovered more
often on the second attempt. The calibrated fast reference still passes this
envelope 5/5 while the opposed reference fails 5/5, so this is model behavior,
not a collapsed benchmark contrast.

## Structural and failure evidence

Proactive numerical programs selected blocked matrix computation in 10/16 cases;
the other six used eager global computation that was nevertheless suitable for
the disclosed envelope. Reactive numerical first attempts were eager in 14/16
cases. Generic guidance often mentioned or implemented blocking, but its chosen
geometry did not satisfy the actual envelope: structural labels are explanatory
evidence and never replace execution-derived suitability.

First-pass failure types were:

| Condition | Suitable | Timeout | Kernel OOM kill |
|---|---:|---:|---:|
| P | 24 | 8 | 0 |
| R | 5 | 18 | 9 |
| G | 5 | 15 | 12 |

This distinction is central to the result. Exact contract availability prevented
all first-pass OOM kills in the proactive cohort and strongly improved operational
suitability, while the latency-tight ETL cell demonstrates that disclosure is
an input to planning rather than a guarantee of perfect contract interpretation.

## Infrastructure interruption and resumption

Original slots 65--96 failed before generation with HTTP 429 after the account's
spending cap was reached. They remain archived as infrastructure failures and are
not model outcomes. The replacement manifest was derived before resumption using
only the predeclared rule “provider failure with zero generated attempts.”

After the account cap was corrected, original slot 65 was run first as a
preselected operational canary. Its complete two-attempt artifact chain passed
audit even though its generated programs were unsuitable. The remaining 31 slots
then ran in the original frozen order regardless of that outcome. Each replacement
records the original trajectory it replaces.

## Cost and capacity

The 96 effective Gemini trajectories used 158 provider calls and an estimated
**$4.961744** in API spend, below the frozen $9 provider cap. The dedicated GCP
worker was stopped immediately after collection. No Gemini result was discarded
or regenerated because of its experimental outcome.

## Gate checklist

- [x] Exact 96-slot balanced cohort complete.
- [x] Zero integrity issues in the fail-closed cohort audit.
- [x] Original HTTP 429 artifacts preserved and replacements source-linked.
- [x] No outcome-dependent stopping or replacement.
- [x] API call and cost caps respected.
- [x] Both independent task instances represented in every cell.
- [x] Mixed ETL latency result retained and explained without protocol change.
- [x] Worker stopped after collection.
- [x] Claude and GPT may proceed under their already-frozen manifests.

## Machine-readable sources

- `experiments/09_aamas_contract_bridge/analysis/gemini_e5_complete_audit.json`
- `experiments/09_aamas_contract_bridge/protocol/confirmatory_gemini38.json`
- `experiments/09_aamas_contract_bridge/protocol/confirmatory_gemini38_resume1.json`
- `experiments/09_aamas_contract_bridge/protocol/confirmatory_gemini38_resume1_canary1.json`
- `experiments/09_aamas_contract_bridge/confirmatory/gemini38_budget_ledger.json`
- `experiments/09_aamas_contract_bridge/confirmatory/gemini38_resume1_budget_ledger.json`

