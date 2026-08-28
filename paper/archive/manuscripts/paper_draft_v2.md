# Substrate-Aware AI Agents: Execution Context as a First-Class Input

**Working manuscript v2.** This draft supersedes neither `paper_draft.md` nor
`paper_draft_revised.md`. It is an arXiv-oriented proof-of-concept manuscript:
the claim is ambitious in principle and exact about what the present experiment
demonstrates. Add complete, accurate consenting author names and affiliations
before submission.

## Abstract

An AI agent can know what to do without knowing the environment in which its action
will execute. We call this informational gap *substrate blindness*. We test whether
one small piece of execution context--a RAM and wall-time contract--changes the
program a model chooses before it runs. In a fixed pairwise-distance task, three
frontier provider-configured model IDs generate code either blind or after zero-shot
disclosure of a 128 MB RAM and 10-second wall-time contract; the prompt supplies no
algorithmic recipe and there is no execution-feedback repair. Across 15 included
fresh direct-API pairs, observed process MaxRSS was lower after disclosure in 13 of
14 executable comparisons, and mean wall time was lower for every model cohort.
The resulting programs differed in block size, precision, traversal,
temporary-buffer handling, and input mapping--not merely in superficial budget
checks. A separate 96 MB condition-level sweep finds correct-and-observed-`<=96 MB`
outcomes of 5/5 for GPT, 4/5 for Claude, and 3/5 for Gemini. Measurements are local
macOS process MaxRSS rather than enforced cgroup survival. The result is a
controlled proof of concept: execution context can change an agent's sampled
computational plan, motivating its treatment as a first-class input to agent
planning.

## 1. The problem: agents know the task, not the environment

AI agents increasingly act inside environments with explicit operating contracts:
containers have memory limits, serverless platforms couple resource configuration to
performance and cost, and schedulers use resource declarations to place work.
Kubernetes, for example, schedules from declared CPU and memory requests and
enforces limits [1]; managed container and serverless platforms similarly make
resource configuration operationally consequential [2, 3].

Yet an agent is often asked only for a solution, not told where that solution will
run. A program can be functionally correct yet unsuitable for its deployment
envelope. We call that informational gap **substrate blindness**. The core idea is
that execution context is decision-relevant agent input: memory, time, software
runtime, compute availability, tool reliability, quota, and cost can all change
what a suitable action looks like.

This paper makes the idea concrete in one controlled setting. Before a coding model
chooses an implementation, we disclose a RAM/time contract and observe the program,
its numerical correctness, peak process memory, and wall time. Numerical code
generation is a useful first testbed because it makes the planning decision and its
operational consequence visible in the same artifact.

Our contributions are:

- We formulate substrate blindness as an information problem in agent planning:
  agents should receive execution-relevant context before selecting an action.
- We provide a controlled, zero-shot proof of concept across 15 fresh direct-API
  pairs from three model cohorts, comparing the same task with and without a
  disclosed RAM/time contract.
- We show that disclosure usually changes resource-relevant implementation choices
  and lowers observed MaxRSS, while reporting model-dependent outcomes and exact
  boundary misses rather than hiding them.

## 2. Substrate awareness: a general principle, tested through code generation

Task context answers *what* an agent should do. Execution context describes *where*
and under which operational contract it must do it. Substrate awareness is the
principle that this context should be available while the agent is selecting an
implementation or action, rather than appearing only after failure.

The present experiment tests a deliberately simple static instance: a RAM boundary
and a wall-time target. The prompt does not prescribe blocking, streaming, a data
type, or an algorithm; no model is fine-tuned; and no execution-error correction
loop is used before the evaluated program is generated. This isolates a meaningful
question: does the execution contract itself alter the sampled computational plan?

The broader principle reaches beyond this benchmark. Interpreter/runtime versions,
CPU quotas, accelerator availability, storage/network conditions, tool reliability,
quota, and cost are all potential execution-context inputs. They are proposed
directions, not results claimed by this paper.

## 3. Controlled demonstration

### 3.1 Task and intervention

The task is to load `vectors.npy`, an 8,000 by 1,024 float32 matrix, compute the
sum of all pairwise Euclidean distances, and print `TOTAL_DIST:<value>`. A dense
8,000 by 8,000 intermediate is resource intensive, whereas correct alternatives
can use bounded blocks, symmetry, and in-place operations.

The fresh direct-API protocol uses identical task instructions in two conditions:

- **Blind (A):** task specification only.
- **Disclosed contract (D):** task specification plus `RAM limit: 128 MB` and
  `Execution time limit: 10.0 seconds`.

The primary cohort contains 15 included, predeclared A/D pairs: five each for the
configured provider model IDs `claude-opus-5`, `gpt-5.6-sol`, and
`gemini-3.7-flash`. We report configured API IDs, not immutable model-weight
snapshots. Raw responses, extracted scripts, prompt hashes, dataset hash, metadata,
and profiles are archived for every retained trial [4].

### 3.2 Measurement and interpretation

Each extracted script runs in an isolated local subprocess on macOS 15.5 arm64 with
Python 3.9.6 and NumPy 2.0.2. BLAS-related thread variables are pinned to one
thread. The profiler records wall time, exit status, stdout/stderr, numerical
output, and OS `RUSAGE_CHILDREN` MaxRSS. A program is correct only if its reported
total is within the configured numerical tolerance of an independently computed
reference [5].

The `<=128 MB` and `<=96 MB` labels are observed-MaxRSS classifications of correct,
exit-zero local runs. They are not claims that a Linux cgroup admitted, killed, or
otherwise enforced the process at those boundaries. Likewise, the jointly disclosed
10-second phrase is a wall-time target, not a CPU-quota experiment.

## 4. Results: execution context changes the generated plan

### 4.1 The primary 128 MB paired cohort

Among the 14 executable A/D comparisons, disclosed-contract MaxRSS is lower in 13:
Claude 4/4, GPT 4/5, and Gemini 5/5. Mean wall time is also lower in every cohort.
The central result is not simply that a program sometimes crosses a budget
threshold. It is that a small piece of pre-execution context systematically changes
the generated implementation and its observed resource use.

| Configured model ID | Blind mean MaxRSS | Disclosed mean MaxRSS | Executable-pair RSS direction | Blind mean wall time | Disclosed mean wall time | Correct / observed `<=128 MB` (blind -> disclosed) |
|---|---:|---:|---|---:|---:|---|
| `claude-opus-5` | 256.48 MB* | 107.82 MB | lower 4/4 | 0.9109 s* | 0.3612 s | 0/5 -> 5/5 |
| `gpt-5.6-sol` | 118.63 MB | 64.61 MB | lower 4/5; higher 1/5 | 0.5507 s | 0.3282 s | 4/5 -> 5/5 |
| `gemini-3.7-flash` | 452.36 MB | 158.16 MB | lower 5/5 | 1.0994 s | 0.3561 s | 0/5 -> 2/5 |

`*` Claude blind continuous means exclude the retained non-executable
runtime-compatibility failure; it remains in the 0/5 correctness/threshold
denominator.

![Figure 1: Paired observed MaxRSS for every executable fresh 128 MB A/D pair.](../figures/fresh_128mb_paired_maxrss.pdf)

**Figure 1.** Every executable fresh A/D pair is shown. Lines connect only jointly
executable pairs. The dashed line is the observed 128 MB reference, not an enforced
cgroup boundary. The retained Claude blind runtime-compatibility failure is marked
rather than omitted.

### 4.2 What changed in the programs

The generated programs did not all move from one naive algorithm to one canonical
optimized algorithm. Several blind GPT and Claude programs already used blocking or
symmetry. Disclosure instead changed resource-relevant implementation choices:
block size, precision, traversal extent, temporary-buffer strategy, in-place output
reuse, and input mapping. The complete source-linked audit covers every included
128 MB script and every retained executable 96 MB script [6].

This is why the result matters. The intervention changed the distribution of
computational implementations selected before execution. It did not merely cause
models to emit a superficial budget check, and it does not guarantee exact
compliance for every model or every boundary.

### 4.3 A tighter disclosed boundary

We additionally generated five independently sampled 96 MB-aware programs per
model. These are condition-level observations, not matched three-condition
trajectories, and therefore do not support a per-generation monotonicity claim.
They nevertheless test whether a tighter stated boundary corresponds to a different
sampled implementation distribution.

| Configured model ID | Blind reference: correct / observed `<=96 MB` | 128 MB-aware reference: correct / observed `<=96 MB` | New 96 MB-aware: mean MaxRSS | New 96 MB-aware: correct / observed `<=96 MB` | New 96 MB-aware mean wall time |
|---|---:|---:|---:|---:|---:|
| `gpt-5.6-sol` | 1/5 | 5/5 | 60.88 MB | 5/5 | 0.3582 s |
| `claude-opus-5` | 0/5 | 0/5 | 87.57 MB | 4/5 | 0.3802 s |
| `gemini-3.7-flash` | 0/5 | 0/5 | 118.46 MB | 3/5 | 0.3985 s |

All 15 retained executable 96 MB programs were numerically correct and completed
within the disclosed 10-second target. The misses are informative: one Claude and
two Gemini programs still exceed 96 MB locally. Awareness of a boundary and exact
runtime compliance are separable capabilities.

![Figure 2: Condition-level observed MaxRSS distributions.](../figures/fresh_boundary_sensitivity_maxrss.pdf)

**Figure 2.** Blind and 128 MB-aware cohorts are reference distributions; 96 MB
programs are independently sampled. Every retained executable observation is shown.
Dashed lines are observed-RSS references, not cgroup enforcement.

## 5. Discussion: why this is useful

The evidence supports a simple but consequential design principle: agents should
not have to discover their operating envelope only after an action fails. Providing
an execution contract at planning time can change what they choose to do.

This is not a claim that smaller memory is always preferable. Suitability is defined
by the deployment envelope; more memory can be a sensible choice when it buys
latency or throughput [3]. Nor is the contribution restricted to an artificial
128 MB threshold. The threshold provides a controlled way to observe whether a
model conditions its implementation on information that is otherwise absent from
the task.

The Claude Python 3.9 compatibility incident makes the same idea visible in
software form. The blind source used a Python 3.10-style union annotation and
raised a `TypeError` when evaluated by the pinned Python 3.9 runtime [4]. The RAM/
time experiment is the paper's controlled test; this incident is a concrete
illustration of the broader information gap. Runtime version, like memory, is a
decision-relevant part of the execution environment that an agent should receive
before it generates deployable code.

The main practical implication is therefore not “always minimize memory.” It is
“condition planning on the contract that defines suitability.” For code agents,
that may mean resources and software runtime. For tool-using or multimodal agents,
the relevant contract may eventually include latency, reliability, permissions,
quota, accelerator availability, or cost.

## 6. Scope and next tests

This paper establishes a controlled proof of concept in numerical code generation;
it does not claim universal exact-boundary compliance, cgroup survival, CPU-quota
adaptation, production cost savings, or the effectiveness of telemetry in every
agent domain. The cohorts are small, the 96 MB cohorts are independently sampled,
and the providers expose configured model IDs rather than immutable snapshots.

Those boundaries describe the next experiments, not a defect in the result already
observed. Natural next tests are runtime-version-aware generation, CPU- and
accelerator-aware planning, constrained data pipelines, and real-time telemetry for
tool selection and recovery. Each requires its own success metric and controlled
intervention.

## 7. Artifact availability

The repository preserves frozen manifests, prompt and dataset hashes, configured
provider metadata, raw responses, extracted scripts, isolated-process profiles, and
analysis code for the displayed results. The fresh direct-API cohort, 96 MB sweep,
complete source-linked audit, and figure renderer are available under
`experiments/06_replication/`, `experiments/08_96mb_cgroup_pilot/`, `docs/`, and
`benchmarks/`. Historical and exploratory artifacts are retained for provenance but
are not pooled with the fresh cohort.

## References

[1] Kubernetes Authors. *Resource Management for Pods and Containers*. Kubernetes
documentation. https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
(accessed 2026-08-27).

[2] Google Cloud. *Configure memory limits for services*. Cloud Run documentation.
https://cloud.google.com/run/docs/configuring/services/memory-limits (accessed
2026-08-27).

[3] Amazon Web Services. *Configure Lambda function memory* and *AWS Lambda
pricing*. https://docs.aws.amazon.com/lambda/latest/dg/configuration-memory.html
and https://aws.amazon.com/lambda/pricing/ (accessed 2026-08-27).

[4] Project artifacts: `experiments/06_replication/RUN_MANIFEST.json`,
`experiments/06_replication/raw/claude-opus-5/opus_rep04_A/`, and
`experiments/08_96mb_cgroup_pilot/RUN_MANIFEST.json`.

[5] Project artifact: `experiments/06_replication/run_replication.py`.

[6] Project artifacts: `docs/13_fresh_code_transformation_audit.md` and
`experiments/06_replication/audit/fresh_code_transformation_audit.json`.
