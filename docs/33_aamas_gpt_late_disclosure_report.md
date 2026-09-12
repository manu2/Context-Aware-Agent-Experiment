# gpt-5.6-sol late-disclosure recovery extension

> This separately frozen extension branches from the same archived R first-attempt failures. Any declared development canary is excluded.

- Integrity audit: **PASS**
- Matched failure states: **24**
- Archived symptom-only recovery suitable: **8/24**
- Late exact-contract recovery suitable: **15/24**
- Transitions: R-fail/L-fail 9, R-fail/L-success 7, R-success/L-fail 0, both suitable 8
- Descriptive exact matched McNemar p-value: **0.015625**
- Provider calls/cost: **24 / $1.519272**

## Stratified outcomes

| Family | Environment | N | Archived R | Late L |
|---|---|---:|---:|---:|
| etl | latency_tight | 8 | 1/8 | 2/8 |
| etl | memory_tight | 8 | 0/8 | 5/8 |
| numerical | latency_tight | 8 | 7/8 | 8/8 |

## Interpretation

For gpt-5.6-sol, the exact execution contract supplied at recovery converted 7 failure states that remained unsuitable under archived symptom-only recovery. 0 archived R successes regressed, 8 states were suitable under both recovery prompts, and 9 remained unsuitable under both. This provider cohort measures the added value of explicit boundary disclosure over authentic failure evidence on identical archived failure states.
