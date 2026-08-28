# Dynamic Agent Harness Telemetry and Self-Aware Agent Loops

**Project:** Aether-Bus / SCAC Phase 2
**Status:** research-and-strategy whitepaper; no new provider trials authorized
**Date:** 2026-08-28
**Evidence boundary:** this document proposes a future dynamic-telemetry study. It
does not convert the repository's static-contract results into evidence for
closed-loop adaptation.

**Canonical status:** this is the consolidated Phase 2 whitepaper. The earlier
`15_dynamic_telemetry_agent_loops_whitepaper.md` is retained as a provenance draft;
its architectural narrative and dynamic-turn-envelope idea are incorporated here,
while unverified prior-art assertions and unpowered numeric effect targets are not.

## Executive summary

Agent harnesses can already observe most of the substrate signals needed for a
self-aware loop: cgroup v2 exposes memory, CPU, I/O, pressure, and limit events;
Linux exposes process and filesystem state; NVML exposes device and per-process
GPU statistics; HTTP clients expose latency, status, and quota headers; and agent
frameworks record model and tool spans. The missing layer is chiefly a control
interface: a causal, bounded, fresh, and trustworthy summary of those observations
that is supplied to the model before its next decision.

Current public documentation for LangSmith and AutoGen emphasizes capture,
debugging, evaluation, and dashboards. OpenTelemetry standardizes agent and tool
spans, while MCP standardizes tool descriptions and structured results. These
facilities make telemetry injection implementable, but neither specification
defines a canonical resource-pressure or tool-health state that a host must place
in model context. Publicly documented frontier stacks should therefore be
classified as **observable by default, adaptive only when application code closes
the loop**. Proprietary systems may do more; lack of public documentation cannot
establish that they do not.

SCAC should test one focused causal claim: supplying a small, truthful, current
telemetry state before a consequential choice improves correct completion under
controlled resource or service degradation. The cleanest first benchmark uses a
deterministic state machine and three independent task families: memory-pressure
adaptation, unreliable-tool routing, and retry termination under quota or service
failure. Each family must compare the same underlying telemetry with (A) no
projection, (B) length-matched neutral context, (C) a compact structured state,
and, on a subset, (D) a natural-language digest. The main outcomes are task
success, operational violations, policy regret, turns, tokens, wall time, and
compound cost. Decisions must be scored at the moment they are made, not inferred
only from final prose.

The recommended architecture is a host-controlled **sense–compress–inject–act–audit**
loop. Raw observations remain outside the prompt in an immutable event log. A
deterministic reducer produces a versioned 4D telemetry vector with provenance,
freshness, uncertainty, and threshold state. The host injects only changed or
decision-relevant fields at a fixed planning boundary. The model cannot edit the
telemetry and cannot disable enforcement. This separates observability,
intervention, and ground-truth enforcement.

## 1. Research position and novelty boundary

The existing SCAC study shows that a truthful pre-execution RAM/time contract can
change generated implementations. Dynamic SCAC asks a different question:

> When the environment changes during a multi-turn trajectory, does projecting a
> current operational state into the next inference improve the agent's next
> action and end-to-end outcome?

The scientific contribution is not the collection of metrics itself. Operating
systems and observability platforms already do that well. Nor is it generic error
feedback: ReAct-style agents and Reflexion already act on tool observations or
linguistic feedback. The proposed contribution is the disciplined transformation
of non-semantic execution state—pressure, throttling, reliability, quota, and
cost—into a minimal model-visible control signal, plus a benchmark that can
attribute behavioral changes to that signal.

Three claims must remain separate:

1. **Extractability:** the harness can measure a signal.
2. **Projection:** the host includes a representation of that signal in the
   model's next inference input.
3. **Adaptation:** the projected signal causally changes a decision and improves a
   predeclared outcome.

Existing public systems strongly establish (1), make (2) programmable, and do not
by themselves establish (3).

## 2. State of the art and prior-art matrix

| Layer or system | Publicly documented signals/capability | Default consumer | Model-visible by default? | SCAC implication |
|---|---|---|---|---|
| Linux cgroup v2 | `memory.current`, `memory.peak`, `memory.events[.local]`, memory/CPU/I/O PSI, `cpu.stat`, `cpu.max`, PID counts, I/O stats | kernel, operators, collectors | No | authoritative enforcement and pressure source |
| Docker | live CPU, memory/limit, network, block-I/O metrics; cgroup discovery | operator/monitor | No | convenient packaging, but read v2 controller files for precise semantics |
| eBPF | programmable kernel event, syscall, scheduler, network, and block-I/O observation | tracing/security systems | No | optional diagnostic source; avoid in the minimal benchmark because it adds privilege and kernel-version variance |
| NVIDIA NVML | device/process memory, utilization, power, temperature, clocks, accounting | scheduler/operator | No | GPU extension after the CPU/memory benchmark is stable |
| OpenTelemetry GenAI conventions | model, agent, tool spans; usage, duration, errors, attributes | telemetry backend | No | common event envelope and correlation IDs, not a decision policy |
| LangSmith/LangChain | prompts, responses, tool calls, traces, metadata, feedback, datasets | developer/evaluator/dashboard | No documented automatic runtime-state reinjection | can archive trajectories and evaluate conditions |
| AutoGen | OpenTelemetry-based agent/tool tracing and message metadata | developer/backend | No documented automatic substrate-state reinjection | instrumentation hook for a future adapter |
| MCP | typed tool schemas, structured/unstructured results, `isError`, annotations and metadata | host and model, according to host policy | Tool result content can be model-visible | suitable transport envelope, but no standard telemetry-health schema or required injection policy |
| Reflexion | scalar or linguistic task feedback stored as episodic text | model on later attempts | Yes | closest conceptual precedent for feedback, but not continuous kernel/tool-health control |
| AgentBench/API-Bank/tool-failure benchmarks | interactive environments, tool outcomes, task success, failure recovery | agent/evaluator | Usually environment observations | methodological precedents; generally do not isolate live substrate telemetry as treatment |

The Linux kernel's cgroup v2 documentation is the normative source for controller
semantics. Two details matter for implementation accuracy. First, current cgroup
v2 CPU throttling counters are reported in `cpu.stat` using fields such as
`nr_throttled` and `throttled_usec`; `throttled_time` is a cgroup v1-era name and
should not be used in the Phase 2 schema. Second, `memory.events.local` is useful
when a trial cgroup has descendants because it excludes descendant aggregation;
the harness should record both local and hierarchical counters when nesting is
possible.

PSI expresses lost execution time due to contention. `some` means at least one
task is stalled; `full` means all non-idle tasks in the measured group are stalled.
The `avg10`, `avg60`, and `avg300` fields are rolling averages, while `total` is a
cumulative stall-time counter. A decision state should use a recent window or a
delta of `total`, never treat the lifetime cumulative value as current pressure.

Tool observability is similarly abundant but retrospective. A wrapper can record
monotonic start/end times, outcome class, HTTP status, retry-after, and provider
quota headers. From these events it can compute a recent failure posterior and
latency quantiles. However, P95 or P99 estimates from a ten-call window are
statistically unstable. The prompt should label small-sample estimates explicitly
and the minimal benchmark should prefer recent success count, consecutive
failures, exponentially weighted latency, and a predeclared circuit state. Tail
quantiles become appropriate only with a larger observation buffer.

## 3. The SCAC 4D telemetry vector

The prior roadmap tuple \(\langle M_{ceiling}, C_{quota}, R_{tool}, V_{token}\rangle\)
is retained, but expanded into four operational namespaces: **hardware, tools,
runtime, economics**. Every value has five metadata properties: source,
observation time, window, confidence/availability, and enforcement status.

```json
{
  "schema": "scac-sst-v0.1",
  "seq": 17,
  "observed_at_ms": 1787884200123,
  "fresh_for_ms": 2000,
  "hardware": {
    "memory": {
      "current_bytes": 112197632,
      "max_bytes": 134217728,
      "headroom_ratio": 0.164,
      "events_delta": {"high": 3, "max": 0, "oom": 0, "oom_kill": 0},
      "psi_some_avg10": 4.21,
      "psi_full_avg10": 0.31,
      "state": "PRESSURED"
    },
    "cpu": {
      "quota_cores": 1.0,
      "nr_throttled_delta": 8,
      "throttled_usec_delta": 124000,
      "psi_some_avg10": 7.3,
      "state": "THROTTLED"
    },
    "gpu": {"available": false},
    "ephemeral_disk": {"used_ratio": 0.42, "free_bytes": 612368384}
  },
  "tools": {
    "remote_a": {
      "window_n": 10,
      "successes": 2,
      "consecutive_failures": 4,
      "latency_ewma_ms": 4180,
      "last_error": "HTTP_503",
      "retry_after_ms": 5000,
      "circuit": "OPEN"
    },
    "local_b": {
      "window_n": 10,
      "successes": 10,
      "latency_ewma_ms": 180,
      "circuit": "CLOSED"
    }
  },
  "runtime": {
    "wall_remaining_ms": 18400,
    "pids_current": 7,
    "pids_max": 64,
    "threads_current": 13,
    "last_exit": {"code": 137, "signal": 9, "class": "CGROUP_OOM"},
    "network": "ENABLED"
  },
  "economics": {
    "context_tokens_remaining": 12400,
    "trajectory_tokens": 18120,
    "estimated_cost_usd": 0.083,
    "budget_remaining_usd": 0.117,
    "rate_limit_remaining": 38,
    "rate_limit_reset_ms": 26000
  },
  "recommended_constraints": [
    "avoid new allocations above 16 MiB",
    "do not call remote_a before circuit closes"
  ]
}
```

`recommended_constraints` are deterministic policy outputs, not hidden
algorithmic advice. They must be generated from frozen threshold rules and tested
in an ablation: raw metrics only versus metrics plus policy labels. This reveals
whether the model needs interpretation or merely access.

### Signal inventory and collection

| Dimension | Minimal signals | Source | Sampling/aggregation |
|---|---|---|---|
| Memory | current, peak, max, `high/max/oom/oom_kill` deltas, PSI | cgroup v2 | 200 ms raw; inject only threshold change or pre-decision snapshot |
| CPU | quota/period, usage, throttled periods/usec, PSI | cgroup v2 | per tool span and pre-decision delta |
| Disk/I/O | free bytes, tmpfs used, read/write bytes, I/O PSI | `statvfs`, mount info, cgroup I/O | 1 s and before large-output action |
| Processes | PID/thread counts, exit code, terminating signal | cgroup `pids.*`, `/proc`, wait status | event-driven |
| GPU | framebuffer used/free, process memory, SM/memory utilization | NVML/DCGM | 250–1000 ms; hardware-dependent |
| Tool health | result class, latency, consecutive failures, retry-after, circuit state | host wrapper/OTel spans | event-driven; recent window and EWMA |
| Quota | remaining/reset/retry-after where provider exposes it | response headers/SDK metadata | each response; unavailable is explicit |
| Tokens/cost | prompt/completion/cache tokens, remaining context, cost estimate | model API + tokenizer/pricing manifest | each inference |

Secrets, raw headers, user data, paths, and unrelated host metrics must be removed
before reduction. Telemetry is untrusted input when it originates from tools; only
the host-signed reducer output belongs in the privileged telemetry slot.

## 4. Representation and injection architecture

### Representation comparison

| Form | Strength | Risk | Recommended use |
|---|---|---|---|
| Compact JSON/key-value | deterministic parsing, easy hashing and ablation | field density can distract; numbers need semantics | primary experimental representation |
| Natural-language digest | easy for models to interpret | wording leaks advice; harder to make conditions equivalent | secondary representation ablation |
| Raw event stream | maximum auditability | prompt bloat, stale evidence, recency confusion | archive only, never primary prompt input |
| Categorical state only | minimal tokens | discards magnitude and uncertainty | low-bandwidth ablation |

The preferred prompt payload is a two-level state: stable contract fields are
sent once, and a delta block contains only changes since the prior decision. A
full checkpoint is re-sent after context compaction or every fixed number of
turns. Fields are ordered deterministically. Units are explicit. Missing values
are `UNAVAILABLE`, not zero.

### Injection point

Use a host-owned telemetry message immediately before a planning/model step and
after the preceding tool result has been normalized. This produces a clean event
order:

```text
model action -> enforced tool execution -> raw event capture -> deterministic
reducer -> telemetry snapshot -> next model decision
```

A mutable system-prompt slot offers high salience but is difficult to reproduce
across APIs. Wrapping telemetry inside every tool observation conflates semantic
results with host state. A dedicated host-authored planning header is therefore
the primary design; system-slot and observation-wrapper placement can be a later
factorial ablation. The telemetry must never contain chain-of-thought or an
evaluator's desired action.

Use a dual-tier prompt layout. Immutable task rules, tool schemas, and telemetry
schema semantics remain in a stable system prefix. Only the current snapshot or
delta appears in the host-authored turn envelope. Besides separating contract
from state, this layout is compatible with provider prefix caching: mutation is
confined to the newest suffix. Cache-hit behavior is provider-specific and must be
measured from reported usage metadata rather than assumed to be 100%.

### Control-plane invariants

- Enforcement remains outside the model and continues if injection fails.
- Each snapshot is hashed and linked to the raw events from which it was reduced.
- The model cannot call a tool to rewrite health or quota state.
- Staleness is explicit; an expired snapshot is not silently reused.
- Thresholds and reducer code are frozen before provider trials.
- Injection occurs only at predeclared decision boundaries, preventing
  outcome-dependent prompting.

## 5. Hypotheses and highest-impact domains

### H1: proactive tool routing

When two functionally equivalent tools differ in current reliability or latency,
a fresh health vector will increase selection of the lower expected-cost tool
without reducing correctness.

Primary decision metric: probability of selecting the lower-regret tool on the
first post-injection choice. End-to-end metrics: completion, wall time, calls, and
cost. Strong controls include shuffled tool names, swapped health states, stale
telemetry, and a truthful equal-health state. This is the cleanest first study
because the action and counterfactual cost are directly observable.

### H2: adaptive resource throttling

When memory headroom falls or PSI/events cross a threshold, dynamic telemetry
will increase bounded actions—smaller chunks, streaming, fewer workers, or
checkpoint/release—before an OOM or deadline violation.

This is scientifically attractive but harder: a model cannot change a running
Python process unless the task exposes controllable parameters or a resumable
workflow. The benchmark must therefore provide an explicit next-chunk/batch action
interface, not pretend that prose can retroactively alter already executing code.

### H3: loop termination and token economics

When a service is unavailable, quota-exhausted, or governed by a retry-after
window, dynamic telemetry will reduce dominated retries and select wait, fallback,
checkpoint, or bounded termination earlier.

The success criterion cannot simply reward fewer calls; premature abandonment is
also a failure. Use policy regret against an oracle with the same information,
plus task utility, elapsed time, token cost, and violation counts.

### Application priority

1. **Data and ML pipelines:** large inputs, explicit batches, costly retries, and
   clear correctness oracles make adaptation measurable.
2. **Serverless agents:** hard memory/time limits and metered duration create
   direct GB-second and timeout costs.
3. **Incident triage:** tools degrade during the task, but safety and external
   validity make this a second-stage domain rather than the first benchmark.
4. **High-throughput multi-agent clusters:** aggregate tool and token costs are
   high; scheduling interactions introduce interference and should follow the
   single-agent causal study.
5. **GPU scientific workflows:** VRAM pressure and checkpointing are important,
   but heterogeneous hardware and driver sampling complicate early replication.

## 6. Three reproducible experimental scenarios

### Scenario 1 — ToolRoute: controlled service degradation

The agent must retrieve and validate a fixed set of records. `remote_a` and
`local_b` return identical, seeded data through the same logical schema. A proxy
injects a predeclared Markov health schedule: healthy, slow, intermittent 503,
and recovered. Latency is virtualized or deterministically delayed; outcomes are
seeded. At each step the agent selects a tool or waits.

- Faults: 0/20/80% failure regimes, 100/800/4200 ms latency regimes,
  `Retry-After` states.
- Oracle: lowest expected completion cost subject to correctness.
- Key score: first-choice routing accuracy and cumulative policy regret.
- Anti-shortcut control: swap tool names and state assignments across replicas.

### Scenario 2 — MemoryGovernor: adaptive chunk execution

The agent controls `chunk_rows`, `worker_count`, and checkpoint/release actions for
a deterministic CSV/array aggregation. The worker executes each chosen chunk in a
cgroup. A background pressure process follows a frozen schedule, changing
available headroom between decisions. The task result is checked against an
external oracle.

- Faults: 25/50/85% initial occupancy; step increase in pressure; optional CPU
  quota reduction.
- Positive control: a calibrated allocation above `memory.max` must increment OOM
  counters and terminate; it is never disabled to make a trial pass.
- Key score: correct completion without `oom_kill`, plus throughput and adaptation
  latency after pressure onset.
- Important design rule: the same pressure process runs in every information
  condition; only the model-visible projection changes.

### Scenario 3 — RetryBudget: quota-aware termination

The agent must complete a multi-step transformation using a remote service with a
fixed token/call budget and a local fallback that is slower but reliable. The
remote service enters a seeded outage and publishes remaining quota and reset
time. The agent chooses retry, wait, fallback, or terminate-with-checkpoint.

- Faults: 429 with reset, 503 without reset, and misleadingly slow success.
- Oracle: dynamic program over the fully known simulator state.
- Key score: utility minus API, token, and elapsed-time cost; forbidden 429 calls;
  redundant retries; premature termination.
- Loop rule: hard maximum turns remains identical across conditions and is not
  itself the treatment.

## 7. Experimental design, controls, and metrics

### Conditions

| ID | Information available at each decision |
|---|---|
| A | ordinary semantic tool result only |
| B | A plus length-matched, decision-irrelevant structured fields |
| C | A plus truthful compact telemetry vector |
| D | A plus semantically equivalent natural-language digest (subset) |
| E | A plus stale or cumulative-only telemetry (diagnostic subset) |

Condition B controls for extra tokens and attention. Condition E tests whether
freshness and recent-window design matter. A falsified or inverted telemetry
condition may measure reliance, but should be isolated as a robustness study
because deliberately misleading the agent changes the safety model.

Use independent stochastic generations unless the provider offers a documented,
effective shared seed. Organizational trial numbers do not justify paired tests.
For deterministic or genuinely seed-matched agents, paired analysis is valid.
Randomize condition order and environment seed; block by model, task instance,
and fault regime. Freeze prompts, simulator, reducer, thresholds, model IDs, and
sampling settings before the main run.

### Primary metrics

Let \(S_i\) be correct task completion, \(V_i\) the count of operational
violations, and \(a_t\) the chosen action at decision \(t\).

- **Operational success:** \(S_i=1\) and no predeclared hard violation.
- **Decision accuracy:** fraction of consequential decisions matching the oracle
  action set.
- **Policy regret:** \(\sum_t [Q^*(s_t,a_t^*)-Q^*(s_t,a_t)]\), using the simulator's
  cost model.
- **Adaptation latency:** decisions or milliseconds from a state transition to
  the first appropriate changed action.
- **Violation counts:** OOM kills, `memory.max` events, invalid 429 calls, deadline
  breaches, and exhausted-budget calls.
- **Trajectory efficiency:** model turns, tool calls, retries, input/output/cache
  tokens, and context utilization.
- **Compound resource cost:**
  \[
  C = \alpha\!\int M(t)dt + \beta\!\int G(t)dt + \gamma T_{api}
      + \delta C_{tokens} + \epsilon C_{violations}.
  \]
  Report physical components separately as MB-seconds/GB-seconds, GPU-seconds,
  API dollars, and token dollars before presenting any weighted composite.

P50/P90/P99 latency should be reported from enough samples and with bootstrap
confidence intervals; do not advertise P99 from a ten-event prompt window.
Correctness and operational success are binary and should receive Wilson intervals
per condition. Use Fisher's exact test or logistic regression for independent
binary samples; McNemar only for genuine matched pairs. For skewed duration, cost,
and regret, report medians and bootstrap intervals and use a predeclared
permutation or rank test. Report standardized effect sizes and multiplicity
correction across the three primary hypotheses.

### Power and sample progression

The skill-level rule of thumb of 10 trials is suitable only for pilot signal and
harness debugging. Paper-grade sample size must be determined by simulation from
the pilot's observed base rate and the minimum effect of interest. A practical
progression is:

1. deterministic unit and calibration tests, with no model calls;
2. one-model pilot, 10–15 independent trajectories per core A/B/C cell;
3. frozen power analysis and exclusion rules;
4. main study, typically 30–50 trajectories per cell if the simulated power
   supports that range;
5. confirmatory model-family replication, reported separately.

All attempted trajectories count. Transport failures, malformed responses,
timeouts, and model refusals are retained and classified under predeclared rules.

## 8. Minimal harness architecture

```text
seeded environment + enforced cgroup
          |
          v
 raw collectors ----> append-only event log ----> deterministic reducer
          |                                      |
          |                                      v
          +---- enforcement               versioned SST snapshot
                                                   |
semantic tool result ------------------------------+
                                                   v
                                      fixed injection renderer
                                                   |
                                                   v
                                           model decision
                                                   |
                                                   v
                                      action validator/executor
                                                   |
                                                   v
                                   external oracle + trajectory audit
```

The minimal implementation does not require eBPF, Kubernetes, a hosted
observability backend, or multi-agent orchestration. Python, a local HTTP fault
proxy, Linux cgroup v2, monotonic clocks, JSONL, and an external evaluator are
sufficient. OpenTelemetry export can be added without making it the source of
truth; canonical artifacts remain local, versioned JSON.

Suggested implementation-repository layout:

```text
benchmarks/dynamic_scac/
  collector.py
  reducer.py
  renderer.py
  runner.py
  schemas/scac-sst-v0.1.json
  scenarios/{toolroute,memory_governor,retry_budget}/
experiments/09_dynamic_scac/
  PROTOCOL.md
  RUN_MANIFEST.json
  calibration/
  raw/<scenario>/<model>/<trial>/
docs/16_dynamic_scac_pilot_report.md
```

Each trial directory should contain the exact prompt/messages, raw model response,
every tool request/result, raw telemetry JSONL, injected snapshots, action log,
container/cgroup manifest, stdout/stderr, exit classification, token usage, and
oracle evaluation. Write-once reservation must occur before the provider call.

### Repository boundary decision

Build the executable Phase 2 harness in a separate repository, provisionally
`scac-dynamic-agent-harness`. Keep this repository as the provenance anchor for
the static-contract study and retain this whitepaper, the cross-study rationale,
and links to frozen Phase 2 releases here.

This boundary is cleaner because the two studies differ in experimental unit,
software architecture, raw artifact schema, threat model, and likely publication
claim. It prevents dynamic trajectories from being silently pooled with the
single-turn cohort and allows the harness to have focused CI, releases, issue
tracking, and container dependencies. It also avoids further crowding a repository
whose `experiments/` tree is already an immutable evidence package.

The split should not sacrifice reproducibility. The new repository should record
this repository's commit SHA as `phase1_basis.commit`; this repository should pin
the new repository's release tag and manifest digest. Shared definitions should
be copied into a versioned schema package or vendored at a pinned revision, not
referenced through a mutable branch. No existing raw artifacts should be moved.

Recommended sequence:

1. Finish and freeze the Phase 2 protocol and SST v0.1 schema here.
2. Create the new repository only when implementation begins.
3. Implement G0–G2 and run zero-cost deterministic calibration there.
4. Tag the first protocol-complete release before any provider pilot.
5. Add reciprocal commit/tag links to both repositories and keep empirical claims
   separate until a later synthesis paper explicitly defines how they relate.

## 9. Phased implementation roadmap

### G0 — specification and threat model

- Freeze the SST schema, unit semantics, freshness rules, and trust boundary.
- Define state-to-label thresholds and the exact injection renderer.
- Predeclare hypotheses, primary metrics, exclusions, and analysis code skeleton.
- Gate: schema fixtures and adversarial untrusted-tool tests pass.

### G1 — collectors and fail-closed enforcement

- Implement cgroup v2 memory/CPU/PSI and process-exit collectors.
- Implement tool-span, quota, token, and cost event collection.
- Add positive controls for memory, timeout, and injected tool faults.
- Gate: an enforcement failure aborts the trial; no provider calls.

### G2 — deterministic scenario simulators

- Build ToolRoute, MemoryGovernor, and RetryBudget with fixed seeds and external
  oracles.
- Hand-author suitable and unsuitable policies for calibration.
- Conduct context-isolated leakage and evaluator-defeat reviews.
- Gate: all scenarios reproduce exactly across clean containers.

### G3 — representation and placement pilot

- Run one configured model on A/B/C, with D on a subset.
- Inspect whether telemetry is noticed, misunderstood, or over-followed.
- Do not tune thresholds on successful model outcomes; revise only for documented
  ambiguity or harness defects and then version the protocol.

### G4 — frozen main study

- Execute the powered matrix with randomized order and independent trials.
- Archive every attempt and publish a machine-verifiable evidence package.
- Analyze each task family separately before any hierarchical aggregate.

### G5 — extensions

- GPU/VRAM pressure, multi-agent shared-resource scheduling, real service outages,
  and telemetry-poisoning robustness.
- Treat these as new protocols, not silent additions to the confirmatory cohort.

## 10. Risks and falsification criteria

- **Prompt-advice confound:** categorical labels may prescribe the action. Measure
  raw-only and label-assisted variants.
- **Attention tax:** extra state can reduce task performance. The neutral control
  and token-normalized efficiency metric make this visible.
- **Stale-state harm:** injection delay can make an otherwise accurate signal
  wrong. Measure snapshot age and include a stale-state diagnostic.
- **Metric gaming:** an agent may minimize retries by quitting. Score task utility
  and regret, not resource use alone.
- **Observer overhead:** high-frequency sampling can alter latency and CPU
  pressure. Measure collector overhead with the model removed.
- **Non-independence:** shared caches, quotas, or service health can couple trials.
  isolate or block them and record global state.
- **Telemetry poisoning:** tool-provided metadata may be adversarial. Only
  host-verified signals enter the privileged block.

The central hypothesis is falsified if truthful telemetry changes prose but not
consequential actions, or if action changes fail to improve predeclared utility
after accounting for the attention and token cost. A negative result would still
be useful: it would show that observability data is not automatically an effective
control input and would identify which representations or models fail to use it.

## 11. Decision and recommended next action

Proceed with a **ToolRoute-first, local, deterministic pilot**. It has the cleanest
counterfactual oracle, requires no cloud spending, and isolates decision-making
from code-generation ability. In parallel only at the implementation level,
construct the shared event log, reducer, and schema so MemoryGovernor and
RetryBudget reuse exactly the same control plane. Do not begin provider trials
until the cgroup/tool-fault positive controls and context-isolated task reviews
pass.

## References and primary documentation

- Linux kernel, [Control Group v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html).
- Linux kernel, [Pressure Stall Information](https://www.kernel.org/doc/html/latest/accounting/psi.html).
- Docker, [Runtime metrics](https://docs.docker.com/engine/containers/runmetrics/).
- NVIDIA, [NVML API Reference](https://docs.nvidia.com/deploy/nvml-api/index.html).
- OpenTelemetry, [Semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
  and [GenAI attribute registry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/).
- Model Context Protocol, [Tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
  and [schema reference](https://modelcontextprotocol.io/specification/2025-06-18/schema).
- LangChain, [LangSmith observability](https://docs.langchain.com/oss/python/langchain/observability).
- Microsoft, [AutoGen tracing and observability](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tracing.html).
- Shinn et al., [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366), 2023.
- Liu et al., [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688), 2023.
- Yao et al., [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629), 2022.
- Li et al., [API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs](https://openreview.net/forum?id=o2HBfgY20b), 2023.
