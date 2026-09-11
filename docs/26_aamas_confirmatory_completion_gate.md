# AAMAS confirmatory completion gate

**Status:** passed on 2026-09-12.

All three frozen provider cohorts are complete and pass the fail-closed evidence
audit with zero integrity issues. The effective confirmatory matrix contains 288
trajectories: 96 each for proactive contract disclosure (P), reactive execution
feedback (R), and generic efficiency guidance (G). Every model, task family,
instance, environment, condition, and repetition cell has its preregistered count.

## Primary result

P produced 64/96 first-pass suitable programs, compared with 14/96 for R and
27/96 for G. Equal-stratum risk differences are +52.1 percentage points for P-R
and +38.5 points for P-G. Both contrasts have two-sided randomization
`p = 9.9999e-06` and Holm-adjusted `p = 1.99998e-05`.

The effect reproduced across all three provider-configured models and in three
of four task-environment regimes. Latency-tight ETL is the preserved boundary
case: all conditions were 1/24 on the first pass.

## Completion and provenance

- Gemini 3.8 Flash: P 24/32, R 5/32, G 5/32 first-pass suitable.
- Claude Sonnet 5: P 16/32, R 1/32, G 2/32 first-pass suitable.
- GPT-5.6 Sol: P 24/32, R 8/32, G 20/32 first-pass suitable.
- The Gemini quota interruption and GPT attempt-2 HTTP 503 remain linked in the
  archive under the predeclared outcome-neutral continuation rules.
- The complete analysis is machine-readable at
  `experiments/09_aamas_contract_bridge/analysis/confirmatory_analysis.json`;
  the generated human-readable report is `docs/28_aamas_confirmatory_results.md`.
- The dedicated Linux worker was stopped after collection.

This gate freezes the empirical result. No treatment, outcome, cohort, task,
threshold, exclusion, or analysis rule may now be changed in response to the
observed results.
