# Exploratory Subagent Pilot Tracker

**Date:** August 2026

**Status:** Completed exploratory proxy pilot
**Scope:** Three isolated subagent configurations, each with one A/D pair. This tracker is separate from the frozen direct-API replication manifest and does not identify provider API models.

---

## Execution Matrix

| Trial ID | Configuration | Condition | Artifact bundle | Status |
|---|---|---|---|---|
| `gpt_pilot_A` | Configuration 1 | A (Blind) | [bundle](raw/gpt-5.6-sol/gpt_pilot_A/) | Complete |
| `gpt_pilot_D` | Configuration 1 | D (Telemetry) | [bundle](raw/gpt-5.6-sol/gpt_pilot_D/) | Complete |
| `gemini_pilot_A` | Configuration 2 | A (Blind) | [bundle](raw/gemini-3.7-flash/gemini_pilot_A/) | Complete |
| `gemini_pilot_D` | Configuration 2 | D (Telemetry) | [bundle](raw/gemini-3.7-flash/gemini_pilot_D/) | Complete |
| `opus_pilot_A` | Configuration 3 | A (Blind) | [bundle](raw/claude-opus-5/opus_pilot_A/) | Complete |
| `opus_pilot_D` | Configuration 3 | D (Telemetry) | [bundle](raw/claude-opus-5/opus_pilot_D/) | Complete |

## Artifact Rules

- Each bundle retains `prompt.txt`, transcript-derived `raw_response.txt`, extracted `script.py`, `metadata.json`, and `profile.json`.
- `metadata.json` records the SHA-256 of its actual `prompt.txt`. The proxy prompts include wrapper metadata and therefore must not be compared to the frozen direct-API prompt hashes in `RUN_MANIFEST.json`.
- `profile.json` is a post-generation, standalone re-profile of the archived script using `run_standalone_script_profile`; it records the exact table metrics, stdout, stderr, exit status, correctness, and budget flags.
- The pilot is exploratory proxy evidence only and is not part of the paper's primary API-model evidence.
