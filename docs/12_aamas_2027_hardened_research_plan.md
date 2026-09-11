# AAMAS 2027 Experiment-First Research and Execution Plan

**Target venue:** AAMAS 2027 Main Technical Track, Generative and Agentic AI (GAAI)  
**Submission deadlines:** abstract October 1, 2026; full paper October 8, 2026  
**Technical freeze:** September 24, 2026  
**Protected review window:** September 25–October 1 (internal/IP review)  
**Protected contingency window:** October 2–8 (approval latency, final audit, submission)  
**Status:** authoritative implementation plan; supersedes the earlier four-arm/400-trajectory draft in this file

## 1. Objective and scope lock

The paper will evaluate a concrete agent-system proposition:

> The effective execution contract is decision-relevant state. Making that state
> observable before implementation selection enables autonomous coding agents to
> choose programs suited to the target operating envelope and reduces the work
> required to discover constraints through failed execution.

The study is not a prompt-wording comparison. It contributes a minimal reusable
**Execution Contract Bridge**, an autonomous generate–execute–recover loop, and a
controlled evaluation of when and how an agent receives target-environment state.

The submission is bounded to two calibrated task families; two execution
environments per family; three primary information conditions; three model
configurations spanning three provider families;
authentic Linux container/cgroup evidence; and complete trajectory provenance.
No new task, adapter, condition, model, or framework integration may enter the
primary matrix after the pilot gate.

## 2. Build-once rule

The pilot must use the same interfaces, artifact schema, execution engine,
scorers, and directory layout as the final experiment. Early implementations may
be narrow, but they must not be parallel throwaway scripts.

### 2.1 Production-shaped vertical slice

```text
Target specification
    -> SubstrateTargetAdapter.inspect()
    -> RawSubstrateEvidence
    -> ContractCompiler.compile()
    -> ExecutionContract
    -> condition-specific context renderer
    -> GenerationBackend.generate()
    -> generated program + provider record
    -> LinuxExecutionBackend.run()
    -> execution observation
    -> AgentLoop decision (stop or one recovery turn)
    -> scorer + immutable trajectory archive
```

The first slice supports one persistent Linux execution worker and one direct-API
provider. The current macOS host has no installed Docker command, so E0 must
select one paper-consistent Linux route: a persistent GCP Linux worker is the
default, while a locally installed container runtime is an acceptable substitute.
Expansion occurs behind the same interfaces, not by rewriting the pilot.

### 2.2 Reuse boundary with Dynamic SCAC

The adjacent `scac-dynamic-agent-harness` project contains tested concepts for
cgroup collection, schema validation, deterministic rendering, provenance, and
trajectory recording. This study will reuse or adapt only the smallest static-
contract primitives needed here, record their source repository and pinned commit
`d98e3610e880ab06421b4e53bb0cd892c1b19170`, and avoid a runtime dependency on
an adjacent working checkout.

Static target contracts remain separate from changing turn-by-turn telemetry.
This paper studies target-state availability before planning; Dynamic SCAC studies
changing operational state during action. Their scenarios and results are not pooled.

## 3. Stable implementation interfaces

These interfaces are frozen before the first direct-API canary.

### 3.1 Target and contract layer

- `SubstrateTargetAdapter`: reads the effective target boundary.
- `RawSubstrateEvidence`: values, units, source paths, observation time,
  availability, and target identity; no environment-variable or credential dump.
- `ContractCompiler`: deterministic projection into a compact contract.
- `ExecutionContract`: versioned memory, wall-time, CPU, runtime, and package
  policy fields with provenance.
- `ContractRenderer`: stable model-visible representation.

Only the Linux execution adapter is required. A clean adapter interface plus
conformance fixtures demonstrates extensibility; cloud, VMware, Kubernetes, and
macOS adapters are not required for this submission.

### 3.2 Generation layer

`GenerationBackend` has two implementations from the beginning:

- `DirectAPIBackend`: empirical generation with complete request metadata;
- `ImportedResponseBackend`: imports a context-isolated sub-agent response or
  saved fixture into the identical response/artifact schema.

The imported backend is permanent test and replay infrastructure. It validates
parsing, execution, scoring, and archival without API spend. Imported/sub-agent
outputs are labeled `development_only` and never enter the paper's results.

### 3.3 Execution and agent-loop layer

- `LinuxExecutionBackend`: isolated workspace, pinned runtime image, wall-time
  limit, cgroup v2 memory/CPU controls, stdout/stderr, exit status, high-water RSS,
  and `memory.events` deltas.
- `AgentLoop`: initial generation followed by at most one recovery generation.
- `TrajectoryRecorder`: append-only events plus a normalized final summary.
- `Scorer`: correctness, suitability, strategy, first-pass/final completion,
  calls, tokens, attempts, MaxRSS, and elapsed time.

Every condition receives authentic supervisor/kernel observations after an actual
failed execution. The harness never fabricates `MemoryError`, exit 137, or a
resource diagnosis not observed by the execution layer.

Three clocks remain distinct:

1. **contract-governed program time**, measured with a monotonic clock around the
   generated child process inside the Linux worker;
2. **enforced timeout**, applied to that same child process and clock domain;
3. **end-to-end trajectory time**, including model latency, transport, worker or
   container orchestration, execution, and recovery.

Worker/container startup is recorded separately and never charged against a
program-only wall-time contract. Main calibration, canary, pilot, and confirmatory
outcomes use Linux measurements; macOS subprocess measurements are development
diagnostics only.

## 4. Primary experimental design

### 4.1 Conditions

| ID | Initial agent state | Recovery observation | Purpose |
|---|---|---|---|
| **P: Proactive contract** | Task plus exact compiled target contract | Authentic execution observation | Proposed system |
| **R: Reactive discovery** | Task only | Authentic observation, without revealing the hidden contract | Discovery through action |
| **G: Generic efficiency** | Task plus balanced memory/time efficiency instruction | Authentic execution observation | Controls for generic optimization prompting |

The same model settings, task, tools, attempt cap, output parser, and execution
backend apply across conditions. Generations are independent samples; index
alignment is bookkeeping, not statistical pairing.

### 4.2 Optional conditions

- **Q: Active inspection:** the agent may call `get_execution_contract()` but is
  not instructed to do so. Run only if the primary evidence leaves acquisition
  timing unresolved and budget remains.
- **U: Safe raw evidence:** sanitized raw substrate evidence versus the compiled
  contract. Run only as a small representation ablation; never expose credentials,
  tokens, complete environment variables, or cloud instance metadata.

An agent skill that mandates substrate inspection is excluded because it would
answer the curiosity question by instruction.

### 4.3 Attempt policy

Each trajectory permits an initial implementation and at most one repair after
authentic execution feedback. It stops on verified success or after the second
execution. This bounds cost while retaining a meaningful reactive baseline.

## 5. Workloads and calibration

### 5.1 Numerical computation: graded sensitivity

Use the existing pairwise-distance family to test changes in tiling, precision,
traversal, and buffer reuse. It demonstrates graded adaptation; it is not an
opposed-envelope case because blocking can improve both memory and speed.

### 5.2 Streaming ETL: opposed envelopes

Use deterministic group aggregation over a generated transaction/log dataset.
One environment is memory-tight with moderate time and should favor bounded
streaming. The other is memory-generous with tight latency and should favor
vectorized or columnar execution.

The previous draft's sizes and limits are calibration hypotheses, not facts.
Handwritten streaming and vectorized references must establish the crossover,
correctness oracle, and safety margins on the actual container before model calls.
The runtime image and allowed package set are part of the task contract. E0 records
idle-interpreter RSS and import-only RSS for every permitted dependency. No 64 MB
or 96 MB ceiling, one-second timeout, Pandas, Polars, or PyArrow policy is frozen
until those Linux measurements demonstrate a feasible, stable envelope.

### 5.3 Model-free calibration gate

For every task instance and environment:

1. generate deterministic inputs and hashes;
2. implement expected-suitable and expected-unsuitable references;
3. run repeated container executions;
4. verify correctness independently;
5. verify memory/timeout enforcement with positive controls;
6. choose thresholds with enough margin to resist scheduler noise;
7. freeze the image digest, dependencies, CPU allocation, and task text.

If the ETL strategies do not reliably cross, redesign the envelope before any
provider call. Calibration is engineering evidence, not a model outcome.

The confirmatory design uses two instances per family. E0 requires only the first
instance from each family. Candidate second instances are a rectangular query-to-
reference distance computation and an access-log aggregation, but they remain
unfrozen until their extra implementation cost and envelope behavior are checked.
Both second-instance specifications, generators, oracles, hashes, and calibration
records must be complete before E4.

## 6. Experiment-early execution gates

### E0a — Core vertical slice (zero API spend)

**Deadline: September 12**

**Status: passed September 11.** The dedicated `aether-aamas-worker` runs Debian
12 on GCP with cgroup v2 memory/CPU controllers. The fixture traversed compilation,
condition rendering, imported generation, direct-SSH Linux execution, scoring,
agent-loop decision, and archival. Positive controls verified `memory.peak`, an
authentic `oom_kill`, and the program timeout. No model API was called.

- stable interfaces and artifact schema implemented;
- Linux execution route selected and capability-checked;
- one fixture completes collection, compilation, generation import, execution,
  scoring, and archival;
- internal program timing and end-to-end timing are independently recorded.

### E0b — Primary-instance calibration lock (zero API spend)

**Deadline: September 13**

**Status: passed September 11 on the hardened runtime.** Runtime/import baselines
and reference profiles are archived. After the worker was hardened, three
envelopes retained 3/3 versus 0/3 separation; the numerical bounded reference had
become fast enough to pass the provisional 4.5-second latency cell. That cell was
recalibrated to 3.0 seconds and passed 5/5 eager-reference versus 0/5
bounded-reference executions. Task text, assets, hashes, runtime, packages,
contracts, and oracle rules are frozen before evidentiary calls.

- one numerical and one ETL instance calibrated in both environments;
- Linux positive controls pass;
- interpreter and permitted-import RSS baselines are archived;
- runtime image, initial package policy, and primary thresholds are frozen;
- prompt-condition differences are machine-diffable;
- replay/import backend completes the entire pipeline.

### E1 — Context-isolated smoke (zero API spend)

**Deadline: September 13**

**Status: passed September 11.** Three independently generated development-only
P/R/G responses completed the identical import, Linux execution, scoring, and
archive path. All were correct and suitable. The P fixture used 23.1 MiB and
1.42 seconds, compared with 83.0–86.7 MiB and 5.54–6.39 seconds for R/G. These
fixtures validate sensitivity and plumbing; they are excluded from empirical results.

Use context-isolated sub-agents to produce representative responses for all three
conditions. Feed unedited responses through `ImportedResponseBackend` and the
production pipeline. This checks prompt clarity, extraction, execution, feedback,
scoring, and archival. The outputs remain development-only.

### E2 — Direct-API canary (real experiment path)

**Deadline: September 14**

Run one economical model on one frozen instance from each family:

`2 task families x 2 environments x 3 conditions x 1 generation = 12 trajectories`

The canary is exploratory and separately labeled, but uses the final API,
execution, and archive path. No manual copying or ad hoc runner is allowed.

**Status: passed after backtracking and correction September 11.** The persistent worker
now runs generated programs under a non-root account with per-run network
isolation, read-only datasets, a 64-process limit, and bounded output capture;
memory, timeout, identity, filesystem, and network controls pass. Gemini 3.8 Flash
is the economical canary model, using its documented default medium thinking
level without deprecated sampling parameters. Canary v3 completed all 12 cells
for $0.293 estimated API spend, but 16/20 calls ended at the inherited 4,096-token
ceiling. It is retained as excluded capacity-calibration evidence. Canary v4 was
frozen with the same cells and a 16,384-token ceiling; it completed for $0.523,
with 8/12 first-pass and final suitable outcomes. Both proactive numerical cells
were suitable while reactive and generic numerical cells were not. All original
ETL cells were suitable because Gemini synthesized a faster streaming parser than
the calibration foil. The ETL task was consequently redesigned before the pilot;
its two revised envelopes each passed 5/5 expected and 0/5 opposed reference
executions. Canary v5 tested only those six changed ETL cells and completed for
$0.235, with 4/6 first-pass and 5/6 final suitable outcomes. The proactive cell
was suitable on the first pass in both opposed environments; the task-only
latency cell remained unsuitable after repair, while generic memory execution
recovered only after an OOM kill. E2 is complete; none of its runs enter the
confirmatory denominator.

### E3 — Non-pooled pilot

**Deadline: September 17**

**Status: primary pilot passed September 11.** The
Gemini 3.8 Flash configuration remains at medium thinking; the output ceiling is
32,768 tokens so the pilot measures model behavior rather than the truncation
seen in canary v3. The randomized manifest contains exactly two independent
generations in every task-family, environment, and P/R/G cell, with a $3 hard
cap. All 24 trajectories and 34 provider calls completed for $1.099; every call
ended with finish reason `STOP`. P achieved 7/8 first-pass and 8/8 final
suitability, compared with 3/8 and 4/8 for R and 4/8 and 4/8 for G. Canary and
pilot artifacts are stored separately and never pooled. The optional U diagnostic
is deferred because no behavioral superiority claim is made for compiled versus
semantically equivalent raw representation.

Run the same 12 cells for two independent generations with the economical pilot
model: **24 trajectories**. Analyze first-pass/final suitability, strategy changes,
P versus G information value, P versus R recovery overhead, calls, tokens, cost,
failure modes, and scoring ambiguity. The pilot does not enter confirmatory results.

Also run a predeclared **six-trajectory U diagnostic** using sanitized raw evidence
that contains the same decision-relevant facts as P plus realistic non-secret
host/target detail. Report the diagnostic regardless of direction. A pilot
difference can justify a frozen confirmatory representation subset; it cannot by
itself establish that compilation improves agent behavior. If no difference is
observed, the compiler remains an engineering contribution for normalization,
provenance, precedence resolution, and safe disclosure.

### E4 — Main-protocol freeze

**Deadline: September 18**

Freeze model IDs/settings, task instances, conditions, sample size, stopping rules,
endpoints, exclusions, replacements, analysis, and maximum spend. No result-driven
prompt or threshold changes are allowed after this gate.

**Status: passed September 11.** Authenticated read-only lookups confirm
access to `gpt-5.6-sol` and `claude-sonnet-5`. Their current provider interfaces
are implemented with explicit medium effort, no unsupported sampling controls,
raw response/usage retention, and fail-closed ledgers. One development-only
end-to-end canary per provider completed through the production path. GPT-5.6 Sol
was first-pass suitable for $0.0664. Claude Sonnet 5 returned two complete
generations for $0.0739; the first timed out and the repair was OOM-killed. Both
development outcomes are retained and excluded from confirmatory estimates. The
Gemini pilot's observed billing supersedes the pre-pilot token assumptions below;
the strategy codebook is frozen. Both secondary instances passed all four
model-free envelopes 5/5 expected versus 0/5 opposed after one preserved,
pre-generation ETL threshold correction. The fixed design uses `N=4`: 288
trajectories, 96 per condition, and provider budget caps totaling $30. The
analysis plan and execution-critical source hashes are frozen before main calls.

Both instances per task family must have frozen generators, task text, oracles,
hashes, container image, package policy, and calibrated envelopes at this gate.

### E5 — Confirmatory campaign

**Execution window: September 19–22**

Frozen confirmatory design:

`2 families x 2 instances x 2 environments x 3 conditions x 3 models x N=4 = 288 trajectories`

With two generations maximum, 288 trajectories have a hard ceiling of 576 model
calls; stop-on-success normally reduces this.

The planned confirmatory configurations are GPT-5.6 Sol, Claude Sonnet 5,
and Gemini 3.8 Flash. Final identifiers and settings freeze at E4. They are all full-matrix cohorts; none is relegated to a
post-hoc confirmation subset.

### E6 — Evidence and technical freeze

**Deadline: September 24**

- complete attempted-run ledger, including provider/parser failures;
- immutable responses, generated programs, execution logs, and hashes;
- rerunnable scorer and analysis;
- figures/tables generated only from archived summaries;
- complete anonymous draft and internal-review package.

No empirical scope is added after this date.

## 7. Endpoints and analysis

Primary endpoints are verified first-pass environment suitability, final completion
within two attempts, and environment-appropriate strategy selection. Secondary
endpoints are calls/tokens, failed executions, recovery latency, MaxRSS, program
time, exceedance magnitude, and structural implementation choices.

Analysis rules:

- treat generations as independent observations, not artificial pairs;
- report denominators and Wilson intervals for binary outcomes;
- compare conditions using exact or permutation methods stratified by frozen
  model/task/environment cells;
- use stratified permutation or bootstrap intervals for continuous outcomes;
- freeze the strategy taxonomy/classifier before confirmatory generation and
  preserve manual adjudications;
- report effect sizes and uncertainty; never promise a p-value in advance.

## 8. Cost controls

The pilot records provider-billed tokens and monetary cost. Before E4:

`projected main cost = pilot mean cost per trajectory x planned trajectories x 1.5`

The author sets a hard ceiling. The runner refuses a request after the manifest's
call or budget limit. Use one economical model for smoke/pilot, all three frozen
model configurations for the full matrix, bounded completions, and a single
executable deliverable. Never rerun a valid but inconvenient outcome.

### 8.1 Planning estimate before the pilot

The following is retained as the **superseded pre-pilot planning estimate**. For
budgeting only, it assumed an average trajectory consumes 2,300 input tokens and
2,800 output/reasoning tokens, while the two-attempt ceiling consumes 4,300 input
and 4,000 output/reasoning tokens. The confirmatory manifests cap each generation
at 32,768 output tokens. As of September 11, 2026, the standard per-million-token input/output
rates used here are Gemini 3.8 Flash $0.75/$3.75 through December 31, 2026,
Claude Sonnet 5 $2/$10,
GPT-5.6 Sol $4/$20, and Claude Opus 5 $5/$25; batch, caching, and fast-tier
discounts or premiums are excluded. For the superseded 360-trajectory planning
matrix, the estimated raw inference cost was about **$13.20** at the average-token
assumption and **$19.68** if every trajectory reached the two-attempt token ceiling.
Pairwise alternatives are retained below only as planning provenance:

| Main-model pairing | Expected raw inference cost | Two-attempt upper scenario |
|---|---:|---:|
| Gemini 3.8 Flash + Claude Sonnet 5 | about $5–6 | about $8–9 |
| Gemini 3.8 Flash + GPT-5.6 Sol | about $9–10 | about $14 |
| GPT-5.6 Sol + Claude Sonnet 5 | about $12 | about $18 |
| GPT-5.6 Sol + Claude Opus 5 | about $18 | about $27 |

The 12-trajectory canary and 24-trajectory pilot added modest
volume when run on the economical model. The approved end-to-end API **hard cap is
$30**, including those gates and contingency. Optional Q, any confirmatory U
subset, or additional models require a separately declared budget before calls.
The official rates and account tier are rechecked at E4, and provider-reported
pilot usage replaces all token assumptions.

### 8.2 Frozen post-pilot budget and provider order

E4 freezes 288 confirmatory trajectories: 96 each for Gemini 3.8 Flash,
GPT-5.6 Sol, and Claude Sonnet 5. Observed pilot/canary billing projects a
two-attempt campaign cost of **$26.05**; the provider manifests enforce an
aggregate **$30** ceiling ($9 Gemini, $13 OpenAI, $8 Anthropic).

Gemini 3.8 Flash runs first because it is the least expensive approved provider
and has already passed the development pilot. After its full cohort completes,
the campaign pauses for a conference-calibrated review of methodology, condition
effects, completeness, and artifact integrity. GPT and Claude calls begin only
after that review supports proceeding. The gate corrects validity problems but
does not add unrelated systems scope or optimize away unfavorable valid outcomes.
It minimizes avoidable spend without changing the frozen matrix, stopping rule,
or analysis.

Keep the persistent Linux worker stopped outside calibration and campaign windows.
Reserve up to **$10 of GCP credit** for VM compute, disk, and transfer; record the
actual billing export separately from model inference cost.

## 9. Artifact layout

```text
experiments/09_aamas_contract_bridge/
├── protocol/               # manifest, prompts, tasks, analysis plan
├── fixtures/
├── calibration/
├── development_smoke/
├── api_canary/
├── pilot/
├── confirmatory/
└── reports/
```

Each trajectory contains the manifest, rendered context, raw provider response,
request metadata, extracted program, execution attempts, cgroup evidence, score,
event log, and hashes. Cohort directories remain visibly separate.

## 10. Delivery calendar

| Date | Deliverable |
|---|---|
| **Sep 11** | Plan and scope frozen |
| **Sep 12** | E0a production-shaped vertical slice and Linux capability check |
| **Sep 13** | E0b primary calibration and E1 imported-response smoke |
| **Sep 14** | 12-trajectory direct-API canary |
| **Sep 15** | Canary audit and validity-critical repairs only |
| **Sep 16–17** | 24-trajectory non-pooled pilot and cost/effect analysis |
| **Sep 18** | Main protocol, statistics, models, and spend frozen |
| **Sep 19–22** | Confirmatory execution |
| **Sep 23–24** | Analysis, manuscript, artifact, and technical freeze |
| **Sep 25–Oct 1** | Protected internal/IP review; abstract due Oct 1 |
| **Oct 2–8** | Protected contingency and final submission |

Manuscript structure and artifact documentation can proceed in parallel, but
results prose is generated only after its evidence is frozen.

## 11. Explicitly deferred work

- universal cloud/VMware/Kubernetes/macOS adapter coverage;
- multi-tenant resource slicing or host sandbox governance;
- an agent skill that mandates substrate inspection;
- dynamic telemetry, stale state, tool reliability, token pressure, and quota
  scenarios from Dynamic SCAC;
- a third task family, including runtime compatibility;
- a second agent framework or portability demonstration;
- packaging polish beyond the experiment and anonymous artifact needs.

## 12. Stop and pivot rules

Stop rather than expand if a paper-consistent Linux worker is unavailable by E0a;
model-free calibration cannot produce reliable ETL opposition; authentic feedback
cannot be captured; the pilot shows only superficial
acknowledgement with no interpretable change across both families; projected cost
exceeds the frozen ceiling; E4 misses September 18; or the evidence package cannot
freeze by September 24.

If the autonomous-trajectory contribution does not survive the pilot, preserve
the reusable infrastructure and redirect it to a later software-engineering study.
Do not rescue the submission by adding uncontrolled conditions.

## 13. Completion state and next action

The full frozen campaign is complete: 288/288 effective trajectories across
Gemini 3.8 Flash, Claude Sonnet 5, and GPT-5.6 Sol pass the fail-closed evidence
audit. The deterministic confirmatory analysis, generated report, vector figures,
and anonymous AAMAS manuscript are present. No additional primary generation is
planned. The deterministic anonymous supplementary artifact contains the frozen
protocol, harness, effective trajectories, preserved interruption slots, analysis,
and disclosure while omitting provider transport metadata. Insert the OpenReview
submission ID when assigned, rebuild the PDF and supplement, and run
`benchmarks/verify_aamas_submission.py --release` before upload.
