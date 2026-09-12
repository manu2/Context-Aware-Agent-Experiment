# claude-sonnet-5 late-disclosure recovery extension

> This separately frozen extension branches from the same archived R first-attempt failures. Any declared development canary is excluded.

- Integrity audit: **PASS**
- Matched failure states: **31**
- Archived symptom-only recovery suitable: **8/31**
- Late exact-contract recovery suitable: **13/31**
- Transitions: R-fail/L-fail 18, R-fail/L-success 5, R-success/L-fail 0, both suitable 8
- Descriptive exact matched McNemar p-value: **0.0625**
- Provider calls/cost: **31 / $0.572114**

## Stratified outcomes

| Family | Environment | N | Archived R | Late L |
|---|---|---:|---:|---:|
| etl | latency_tight | 7 | 0/7 | 0/7 |
| etl | memory_tight | 8 | 8/8 | 8/8 |
| numerical | latency_tight | 8 | 0/8 | 3/8 |
| numerical | memory_tight | 8 | 0/8 | 2/8 |

## Interpretation

For claude-sonnet-5, the exact execution contract supplied at recovery converted 5 failure states that remained unsuitable under archived symptom-only recovery. 0 archived R successes regressed, 8 states were suitable under both recovery prompts, and 18 remained unsuitable under both. This provider cohort measures the added value of explicit boundary disclosure over authentic failure evidence on identical archived failure states.
