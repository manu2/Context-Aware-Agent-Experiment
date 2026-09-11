# AAMAS E2–E3 report: hardened canary and non-pooled pilot

## Scope

This report records development gates only. Canary and pilot trajectories validate
the protocol and inform the confirmatory freeze; they are never pooled with the
confirmatory evidence.

## Hardened execution boundary

Before further provider calls, the Linux worker was changed so generated programs
run as the dedicated non-root `aether-runner` account in a fresh network namespace.
Datasets and the Python runtime are root-owned and read-only, each execution has a
64-process ceiling, and stdout and stderr are capped at 1 MiB each. Archived
controls verify cgroup memory metering, kernel OOM kills, timeouts, non-root
identity, dataset non-writability, and network isolation.

The hardened runtime changed numerical timing enough to invalidate the provisional
4.5-second latency envelope. A 3.0-second replacement passed 5/5 eager-reference
and 0/5 bounded-reference executions. No model call was made until that replacement
was archived.

## Canary history

- V1 is excluded because a VM restart cleared the temporary worker path before any
  generated program launched. The 12 provider responses and $0.103 estimated spend
  remain archived.
- V2 completed on the earlier Gemini 3.7/runtime configuration for $0.182. It is
  development evidence only.
- V3 adopted Gemini 3.8 Flash and the hardened runtime. Sixteen of 20 calls ended
  at the inherited 4,096-token ceiling, so the run is retained as excluded capacity
  calibration. Estimated spend was $0.293.
- V4 repeated the 12 cells at a 16,384-token ceiling. It cost $0.523 and produced
  8/12 first-pass and final suitable outcomes. Both proactive numerical cells were
  suitable; reactive and generic numerical cells were not.
- V4 also showed that Gemini could synthesize an optimized `csv.reader` program
  much faster than the original `DictReader` calibration foil. The original ETL
  latency opposition was therefore rejected rather than carried into the pilot.
- The revised ETL conditional weighted-aggregation task preserved the dataset but
  made per-row computation consequential. Pandas measured approximately 1.03 s and
  271 MiB; optimized streaming measured 1.83–2.03 s and 4.3 MiB. The 128 MiB/4.0 s
  and 512 MiB/1.4 s environments each passed 5/5 expected and 0/5 opposed reference
  executions.
- V5 tested only the six revised ETL cells. It cost $0.235 and achieved 4/6
  first-pass and 5/6 final suitability. Proactive disclosure passed both opposed
  environments on the first attempt.

## Non-pooled pilot

The frozen Gemini 3.8 Flash pilot used medium thinking, no deprecated sampling
parameters, a 32,768-token output ceiling, two independent generations in every
task/environment/P-R-G cell, at most one repair, and a $3 hard cap.

| Condition | N | First-pass suitable | Final suitable | Provider calls |
|---|---:|---:|---:|---:|
| P: proactive contract | 8 | 7/8 | 8/8 | 9 |
| R: reactive discovery | 8 | 3/8 | 4/8 | 13 |
| G: generic efficiency | 8 | 4/8 | 4/8 | 12 |

All 24 trajectories completed. All 34 calls ended with provider finish reason
`STOP`; no pilot response hit the token ceiling. Estimated API cost was $1.099.

The numerical task produced the clearest separation: proactive disclosure was
suitable in 4/4 trajectories, while reactive discovery and generic efficiency
were each suitable in 0/4. In ETL, all conditions eventually completed, but the
implementation distribution responded to the environment. Both proactive
memory-tight programs used standard-library streaming, while both proactive
latency-tight programs used Pandas. The task-only latency programs initially used
streaming; one timed out and repaired to Pandas.

These are pilot observations rather than confirmatory estimates. They establish
that the pipeline is sensitive to the intended planning distinction and justify
advancing to a model- and analysis-freeze stage. The confirmatory analysis must
remain stratified by model, task, and environment.

## Gate decision

E3 primary pilot passes. The optional raw-versus-compiled representation diagnostic
is deferred because the current contribution does not claim that compiled wording
outperforms semantically equivalent raw evidence. The compiler is evaluated as a
normalization, provenance, precedence, and disclosure-safety mechanism. This keeps
the confirmatory study focused on whether decision-relevant execution context is
available before plan selection.

Before E4, the remaining required work is to validate the exact Claude and OpenAI
provider configurations, use their observed billing to select a feasible fixed
sample size under the total budget, freeze the strategy-feature taxonomy, and
complete/calibrate the second task instance in each family.
