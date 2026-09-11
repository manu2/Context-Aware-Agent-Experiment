# AAMAS E0a Vertical-Slice Report

**Date:** September 11, 2026  
**Status:** Passed  
**Provider API spend:** $0

## What passed

- Dedicated GCP worker: Debian 12, Linux 6.1, cgroup v2, memory and CPU controllers.
- Bounded infrastructure: `e2-standard-2`, 20 GB disk, automatic stop after six hours.
- Production-shaped path: evidence -> contract -> P/R/G renderer -> imported
  response -> extracted program -> direct-SSH Linux execution -> score ->
  agent-loop decision -> immutable trajectory archive.
- Successful fixture: `TOTAL:5050`, correct, within 64 MiB and five seconds.
- Memory measurement control: a 16 MiB allocation produced a 19,681,280-byte
  cgroup `memory.peak`, below the 64 MiB ceiling.
- Enforcement control: a 96 MiB allocation under 48 MiB produced an authentic
  `memory.events` increment (`oom=1`, `oom_kill=1`) and peak of 50,331,648 bytes.
- Timeout control: a three-second sleep under a one-second contract was terminated
  and classified as timed out.
- Five local interface tests and repository whitespace validation passed.

## Preserved development failures

Two early development attempts are retained and explicitly excluded. They stopped
before an execution observation because the new experiment cgroup parent initially
lacked delegated controllers. The worker was corrected by enabling `memory` and
`cpu` on the parent before creating each run cgroup. A later transient Compute API
502 motivated direct SSH for per-trajectory transport; cloud API access is no
longer on the execution hot path.

## Evidence

- Successful trajectory: `experiments/09_aamas_contract_bridge/development_smoke/e0a-20260911T134340Z/`
- Positive controls: `experiments/09_aamas_contract_bridge/calibration/e0a_positive_controls.json`
- Frozen manifest: `experiments/09_aamas_contract_bridge/protocol/manifest.json`

The next gate is E0b: calibrate one numerical and one ETL instance in both target
environments, measure interpreter/import baselines, and freeze the primary runtime
and package policy before any model call.
