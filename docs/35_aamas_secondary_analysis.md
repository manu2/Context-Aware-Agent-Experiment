# AAMAS secondary and robustness analysis

> Deterministic analysis of the frozen 288-trajectory confirmatory matrix and the separately frozen 82-state matched late-disclosure extension.

## Removal robustness

| Contrast | Full RD | Leave-one-model range | Leave-one-instance range | Leave-one-family range | Leave-one-environment range | Leave-one-stratum range |
|---|---:|---:|---:|---:|---:|---:|
| P minus R | 52.1 pp | 48.4--54.7 pp | 47.9--56.2 pp | 39.6--64.6 pp | 35.4--68.8 pp | 50.0--54.3 pp |
| P minus G | 38.5 pp | 28.1--51.6 pp | 31.2--45.8 pp | 22.9--54.2 pp | 25.0--52.1 pp | 35.9--41.3 pp |

All leave-one-full-stratum estimates remain positive for both primary contrasts.

## Matched recovery timing

Across the same 82 archived first-failure states, symptom-only recovery succeeded in **19/82** cases and late exact-contract recovery in **53/82**. The matched transitions were **35 improvements**, **1 regression**, **18 shared successes**, and **28 shared failures** (exact two-sided McNemar p = **1.0768417e-09**).

## Interpretation

The primary first-pass effect survives removal of any one provider configuration, task instance, family, environment type, or individual full stratum. The matched recovery extension independently shows that exact execution state remains highly actionable after failure: it substantially outperforms symptom-only feedback on identical archived failure states. Together these analyses separate two benefits of the same contract representation: proactive disclosure prevents unsuitable initial actions, while persistent disclosure makes the bounded recovery step markedly more effective.
