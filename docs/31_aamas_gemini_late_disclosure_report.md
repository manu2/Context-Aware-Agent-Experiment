# gemini-3.8-flash late-disclosure recovery extension

> This separately frozen extension branches from the same archived R first-attempt failures. Any declared development canary is excluded.

- Integrity audit: **PASS**
- Matched failure states: **27**
- Archived symptom-only recovery suitable: **3/27**
- Late exact-contract recovery suitable: **25/27**
- Transitions: R-fail/L-fail 1, R-fail/L-success 23, R-success/L-fail 1, both suitable 2
- Descriptive exact matched McNemar p-value: **2.9802322e-06**
- Provider calls/cost: **27 / $1.206229**

## Stratified outcomes

| Family | Environment | N | Archived R | Late L |
|---|---|---:|---:|---:|
| etl | latency_tight | 8 | 1/8 | 6/8 |
| etl | memory_tight | 3 | 2/3 | 3/3 |
| numerical | latency_tight | 8 | 0/8 | 8/8 |
| numerical | memory_tight | 8 | 0/8 | 8/8 |

## Interpretation

For gemini-3.8-flash, the exact execution contract supplied at recovery converted 23 failure states that remained unsuitable under archived symptom-only recovery. 1 archived R successes regressed, 2 states were suitable under both recovery prompts, and 1 remained unsuitable under both. This provider cohort measures the added value of explicit boundary disclosure over authentic failure evidence on identical archived failure states.
