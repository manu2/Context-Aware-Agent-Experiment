# GPT-5.6 Sol and Claude Sonnet 5 provider canaries

**Date:** 2026-09-11  
**Status:** completed; development-only and excluded from confirmatory estimates

Authenticated read-only model lookups first confirmed access to the exact
`gpt-5.6-sol` and `claude-sonnet-5` identifiers. The request configurations were
then committed before calls. Each provider received the same proactive-contract
prompt for the primary numerical memory-tight cell and used the production
generation, Linux execution, scoring, recovery, and archive path.

| Configuration | Effort | Calls | Cost | First pass | Final | Execution evidence |
|---|---|---:|---:|---:|---:|---|
| GPT-5.6 Sol | medium | 1 | $0.0664 | suitable | suitable | correct; 58.5 MiB; 2.085 s |
| Claude Sonnet 5 | medium, adaptive thinking | 2 | $0.0739 | unsuitable | unsuitable | attempt 1 timed out; attempt 2 was kernel OOM-killed |

Both APIs returned complete, non-truncated responses and complete usage records.
The Claude outcome is a valid unfavorable development observation, not an API or
worker failure. No replacement or rerun was made. Two earlier launch attempts
failed before provider generation because the restarted VM's direct SSH identity
was not yet refreshed; they consumed no provider calls and created no trajectory.
The gcloud-managed host alias restored strict host-key verification before the
frozen canaries ran.

At observed canary/pilot rates, a two-attempt worst-observed projection for
`N=5` is above the original $30 campaign target, while `N=4` projects near $26
before a modest contingency. The final E4 sample-size decision will therefore use
power analysis plus the second-instance calibration, rather than the superseded
pre-pilot token assumptions.
