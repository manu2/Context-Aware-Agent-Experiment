# AAMAS E5 Claude Sonnet 5 Confirmatory Gate

**Date:** 2026-09-12  
**Status:** Complete; integrity gate passed; GPT cohort approved  
**Model:** `claude-sonnet-5`  
**Evidence:** 96 confirmatory trajectories, 173 provider calls, two task families,
two independent instances per family, two opposed execution envelopes, and three
planning conditions

## Decision

Proceed with the frozen GPT-5.6 Sol cohort without changing the protocol. All 96
Claude trajectories are complete, and the fail-closed audit reports zero prompt,
manifest, model, retry, artifact, or scoring inconsistencies.

## Cohort-level outcomes

| Condition | First-pass suitable | Final suitable | Provider calls |
|---|---:|---:|---:|
| Proactive exact contract (P) | 16/32 (50.0%) | 22/32 (68.8%) | 48 |
| Reactive execution observation (R) | 1/32 (3.1%) | 9/32 (28.1%) | 63 |
| Generic efficiency guidance (G) | 2/32 (6.3%) | 7/32 (21.9%) | 62 |

The descriptive first-pass risk differences are **+46.9 percentage points** for
P versus R and **+43.8 points** for P versus G. Formal multi-model inference
remains locked until the GPT cohort is also complete.

## Stratified outcomes

| Task family | Environment | P first/final | R first/final | G first/final |
|---|---|---:|---:|---:|
| Numerical | Memory-tight | 6/8, 6/8 | 0/8, 0/8 | 0/8, 1/8 |
| Numerical | Latency-tight | 1/8, 7/8 | 0/8, 0/8 | 0/8, 0/8 |
| ETL | Memory-tight | 8/8, 8/8 | 0/8, 8/8 | 2/8, 6/8 |
| ETL | Latency-tight | 1/8, 1/8 | 1/8, 1/8 | 0/8, 0/8 |

The first-pass result is not confined to one task. Proactive disclosure dominates
both numerical envelopes and is perfect in memory-tight ETL. In numerical
latency-tight cells, six of seven initially unsuitable proactive trajectories
recover after one authentic observation, while neither comparison condition
does. In memory-tight ETL, reactive feedback eventually repairs all eight
programs but requires a failed first execution in every case; proactive context
avoids that loop in all eight.

Latency-tight ETL again remains difficult across conditions. This replicates the
Gemini boundary: the disclosed deadline changes planning but does not ensure that
the model selects a sufficiently fast implementation.

## Structural and failure evidence

All 16 proactive numerical first attempts used blocked matrix computation. The
same structural label also appeared in all 16 generic attempts and 13/16 reactive
attempts, demonstrating why execution-derived suitability is the primary outcome:
the existence of blocking alone does not determine whether tile geometry,
precision, and traversal choices fit a concrete envelope.

First-pass failure types were:

| Condition | Suitable | Timeout | Kernel OOM kill |
|---|---:|---:|---:|
| P | 16 | 14 | 2 |
| R | 1 | 16 | 15 |
| G | 2 | 16 | 14 |

Proactive disclosure sharply reduces first-pass kernel OOM kills and increases
operational suitability. Reactive execution evidence remains valuable for repair,
especially in memory-tight ETL, but it incurs the failed first execution that the
proactive condition is designed to avoid.

## Cost and capacity

The cohort used 173 provider calls and an estimated **$1.980382** in API spend,
well below the frozen $8 cap. The dedicated GCP worker was stopped immediately
after the complete audit.

## Gate checklist

- [x] Exact 96-slot balanced cohort complete.
- [x] Zero integrity issues in the fail-closed cohort audit.
- [x] No outcome-dependent stopping or replacement.
- [x] API call and cost caps respected.
- [x] Both independent task instances represented in every cell.
- [x] Mixed latency-tight ETL result retained without protocol change.
- [x] Worker stopped after collection.
- [x] Frozen GPT cohort approved to proceed.

## Machine-readable sources

- `experiments/09_aamas_contract_bridge/analysis/claude_e5_complete_audit.json`
- `experiments/09_aamas_contract_bridge/protocol/confirmatory_anthropic_sonnet.json`
- `experiments/09_aamas_contract_bridge/protocol/confirmatory_anthropic_sonnet_canary1.json`
- `experiments/09_aamas_contract_bridge/confirmatory/anthropic_sonnet_budget_ledger.json`

