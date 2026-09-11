# E5 Gemini infrastructure interruption and resume rule

**Recorded:** 2026-09-11, after the first provider failure and before any resume call

## What happened

The frozen Gemini 3.8 Flash order completed slots 1–64. All requests beginning at
slot 65 returned HTTP 429, so slots 65–96 contain no model generation. The archive
preserves all 32 failed requests. They are infrastructure exclusions, not
unsuitable agent outcomes.

The raw ledger contains 103 completed calls with estimated cost $3.065830 and 32
unsettled reservations totaling $3.936257. The latter are retained as raw history
and are not interpreted as billed usage. The GCP worker was stopped immediately
after diagnosis.

## Outcome-neutral resume rule

Only the exact 32 slots whose initial generation failed before a provider response
may be regenerated. Their original frozen task, instance, environment, condition,
model configuration, and order are unchanged. Replacements receive new trajectory
identifiers linked to the original failed slot; original records are never edited
or deleted. No completed or unfavorable generated-program outcome is eligible.

The resume begins only after quota/billing access is verified. It stops on the
first provider-level HTTP failure. Gemini must then pass the complete-cohort audit
before Claude or GPT begins.

## Runner amendment

The discovered behavior justified a narrow post-freeze infrastructure repair:

- provider HTTP failures now release local cost reservations while retaining an
  explicit failed ledger entry;
- a provider HTTP failure stops the campaign immediately;
- runner success now requires every scheduled trajectory to be complete, rather
  than merely possessing a summary file.

This amendment changes failure handling only. It does not change prompts,
contracts, tasks, thresholds, model settings, sample allocation, outcomes, or the
analysis plan.

The frozen resume manifest is
`experiments/09_aamas_contract_bridge/protocol/confirmatory_gemini38_resume1.json`.
It contains the exact 32 original execution entries and replacement links, permits
at most 64 completed generation attempts, and caps additional estimated spend at
$5.934170 so total estimated Gemini spend cannot exceed the original $9 ceiling.
