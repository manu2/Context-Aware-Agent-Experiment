# E5 GPT infrastructure interruption and exact-attempt resume

**Recorded:** 2026-09-12, after the provider interruption and before any resume call

## Observed interruption

The frozen GPT-5.6 Sol cohort completed trajectories 1–80. In trajectory 81,
attempt 1 was generated and executed normally: its ETL program timed out under
the 1.4-second latency-tight contract, so the frozen agent loop correctly formed
an execution-feedback repair prompt. OpenAI then returned HTTP 503
`server_is_overloaded` before an attempt-2 response was received. The campaign
stopped fail-closed. This is an infrastructure interruption between attempts,
not a completed trajectory and not an outcome eligible for replacement.

## Frozen recovery rule

Trajectory 81 retains its original identifier, attempt-1 program, execution
observation, score, strategy classification, and exact archived repair prompt.
Recovery may generate **attempt 2 only**, using that archived prompt and the
unchanged frozen model settings. Before recovery, the failed summary is copied
to `infrastructure_interruption_summary.json`; the append-only event history and
all original artifacts remain intact. The recovery tool refuses to run unless:

- the trajectory snapshot exactly matches the frozen GPT manifest;
- the failure is the observed provider HTTP 503;
- exactly one complete attempt exists and authorized a repair;
- the attempt-2 prompt exists; and
- no attempt-2 provider response or program already exists.

After trajectory 81 completes, the original manifest resumes at trajectory 82.
No prompt, task, contract, threshold, condition, allocation, model setting, or
analysis rule changes. Any further provider failure again stops the campaign.

The recovery tool is `benchmarks/resume_aamas_partial_trajectory.py`.
