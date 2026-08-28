# Substrate-Aware AI Agents: Execution Context as a First-Class Input

**Working revision, not yet submission-ready.** Replace this placeholder with
complete, accurate author names and affiliations before submission; arXiv does not
accept anonymous submissions. Prepare and render a final PDF/LaTeX package after
the remaining audit items at the end of this document are complete.

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

## 1. Introduction

AI agents increasingly act inside environments with explicit operating contracts:
containers have memory limits, serverless platforms couple resource configuration to
performance and cost, and schedulers use resource declarations to place work.
Kubernetes, for example, schedules from declared CPU and memory requests and
enforces limits [1]; managed container and serverless platforms similarly make
resource configuration operationally consequential [2, 3].

But an agent is often asked only for a solution, not told where that solution will
run. A program can be functionally correct yet unsuitable for its deployment
envelope. We call that informational gap **substrate blindness**. The broader idea
is that execution context is decision-relevant agent input: memory, time, software
runtime, compute availability, tool reliability, quota, and cost can all change
what a suitable action looks like.

This paper tests one clean, inspectable instance of that idea. Before a coding
model chooses an implementation, we disclose a RAM/time contract and observe the
generated program, numerical correctness, peak process memory, and wall time.
Numerical code generation makes the before-and-after decision visible: reviewers
can inspect both the implementation and its execution outcome.

Our contributions are:

- We formulate substrate blindness as an information problem in agent planning:
  agents should receive execution-relevant context before selecting an action.
- We provide a controlled, zero-shot proof of concept across 15 fresh direct-API
  pairs from three model cohorts, with the same task but blind versus disclosed
  RAM/time context.
- We show that disclosure usually changes resource-relevant implementation choices
  and lowers observed MaxRSS, while retaining the mixed outcomes and exact-boundary
  misses that delimit the claim.

## 2. Substrate Awareness as an Agentic Principle

An agent's task context answers *what* to do. Execution context describes *where*
and *under which operational contract* it must be done. We propose that relevant
execution context should be available while an agent selects an implementation or
action, rather than only appearing after a failure.

This study evaluates a static spatial/temporal instance: a RAM boundary and a
wall-time target. It does not evaluate interpreter/runtime versions, CPU quotas,
GPU/VRAM, storage or network limits, tool reliability, token cost, or dynamic
telemetry. Those dimensions are future controlled studies, not claimed results here.

The intervention is deliberately lightweight: the prompt adds an explicit resource
contract, without prescribing tiling, streaming, data types, or any particular
algorithm; there is no model fine-tuning and no execution-error correction loop
before the evaluated program is generated.

## 3. Experimental Method

### 3.1 Task and conditions

The task is to load `vectors.npy`, an 8,000 by 1,024 float32 matrix, compute the
sum of all pairwise Euclidean distances, and print `TOTAL_DIST:<value>`. A dense
8,000 by 8,000 intermediate is resource intensive, while correct alternatives can
use bounded blocks, symmetry, and in-place operations.

The fresh direct-API protocol uses two conditions with identical task instructions:

- **A, blind:** task specification only.
- **D, disclosed contract:** task specification plus `RAM limit: 128 MB` and
  `Execution time limit: 10.0 seconds`.

The 96 MB extension reuses separately labelled fresh blind and 128 MB-aware cohorts
as reference distributions and adds five new independently generated D programs per
model with `RAM limit: 96 MB` and the same 10-second target. It is not a matched
three-condition experiment.

### 3.2 Generation, provenance, and execution

The primary 128 MB cohort contains 15 included predeclared A/D pairs: five each for
the configured provider model IDs `claude-opus-5`, `gpt-5.6-sol`, and
`gemini-3.7-flash`. The repository records the requested provider IDs, endpoint,
sampling configuration, prompt hash, dataset SHA-256, timestamp, raw response,
extracted script, and profile for each trial [5]. The harness permits up to three
transport/API attempts inside a trial and archives the terminal result; it does not
record every provider request identifier. These identifiers are configured API IDs,
not immutable provider weight snapshots; model availability and aliases
should be checked at reproduction time.

Each extracted script runs in an isolated local subprocess on macOS 15.5 arm64 with
Python 3.9.6 and NumPy 2.0.2. BLAS-related thread environment variables are pinned
to one thread. The profiler records wall time, exit status, stdout/stderr, numerical
output, and OS `RUSAGE_CHILDREN` MaxRSS, with a 60-second watchdog. A program is
correct only if its reported total is within the configured numerical tolerance of
the independently computed reference [6].

`<=128 MB` and `<=96 MB` are observed-MaxRSS classifications of correct,
exit-zero local runs. They are not claims that a Linux cgroup admitted or killed the
process at those boundaries. The 10-second phrase is a disclosed wall-time target,
not a CPU quota; because RAM and time are jointly disclosed, this study does not
isolate the causal contribution of the time phrase.

### 3.3 Counting and response validity

The 15 fresh pairs are included predeclared experimental units. One Claude blind
script (`opus_rep04_A`) is retained as a Python 3.9 runtime-compatibility failure.
Thus it remains
in correctness/threshold denominators, while continuous blind-RSS and wall-time
means for Claude use the four executable blind scripts.

For the 96 MB Claude extension, two initial provider responses were malformed (one
empty and one truncated before a complete program). Both are retained. Before
replacement generation, manifest v1.5 predeclared two identical-prompt replacement
IDs. Five retained executable Claude observations therefore arise from seven
archived response attempts; response validity and resource compliance are reported
separately [7].

## 4. Results

### 4.1 Fresh paired 128 MB cohort

Table 1 reports descriptive cohort summaries. Every included outcome, including the
Claude runtime-compatibility failure and the GPT RSS regression, is retained in the row-level
artifact report [8]. Among the 14 executable A/D comparisons, disclosed-contract
RSS is lower in 13: Claude 4/4, GPT 4/5, and Gemini 5/5. Mean wall time is lower in
all three cohorts.

| Configured model ID | Blind mean MaxRSS | Disclosed mean MaxRSS | Executable-pair RSS direction | Blind mean wall time | Disclosed mean wall time | Correct / observed `<=128 MB` (blind -> disclosed) |
|---|---:|---:|---|---:|---:|---|
| `claude-opus-5` | 256.48 MB* | 107.82 MB | lower 4/4 | 0.9109 s* | 0.3612 s | 0/5 -> 5/5 |
| `gpt-5.6-sol` | 118.63 MB | 64.61 MB | lower 4/5; higher 1/5 | 0.5507 s | 0.3282 s | 4/5 -> 5/5 |
| `gemini-3.7-flash` | 452.36 MB | 158.16 MB | lower 5/5 | 1.0994 s | 0.3561 s | 0/5 -> 2/5 |

`*` The Claude blind mean excludes the retained non-executable runtime-compatibility failure;
that failure remains in the 0/5 correctness/threshold denominator.

The result is not a uniform transition from naive eager code to blocking. All fresh
GPT blind outputs and most executable Claude blind outputs already used some
blocking or symmetry. The disclosed condition instead commonly changed
resource-relevant choices such as block size, data type, extent of traversal,
temporary-buffer strategy, in-place operations, and input mapping. This distinction
matters: substrate awareness changes the distribution of implementations rather
than guaranteeing a single canonical algorithm.

![Figure 1: Paired observed MaxRSS for every executable fresh 128 MB A/D pair. The retained Claude `opus_rep04_A` first-pass runtime failure is marked explicitly.](../figures/fresh_128mb_paired_maxrss.pdf)

**Figure 1.** Paired observed MaxRSS for every executable fresh 128 MB A/D pair.
Lines connect only jointly executable pairs. The dashed 128 MB line is an
observed-RSS reference, not enforced cgroup admission; Claude `opus_rep04_A` is
retained as a first-pass Python 3.9 runtime-compatibility failure.

### 4.2 Boundary sensitivity at 96 MB

Table 2 reports separate condition-level distributions. The 96 MB samples are not
paired with the 128 MB samples; consequently, this table does not support a
per-generation monotonicity claim or a pooled hypothesis test.

| Configured model ID | Blind reference: correct / observed `<=96 MB` | 128 MB-aware reference: correct / observed `<=96 MB` | New 96 MB-aware: mean MaxRSS | New 96 MB-aware: correct / observed `<=96 MB` | New 96 MB-aware mean wall time |
|---|---:|---:|---:|---:|---:|
| `gpt-5.6-sol` | 1/5 | 5/5 | 60.88 MB | 5/5 | 0.3582 s |
| `claude-opus-5` | 0/5 | 0/5 | 87.57 MB | 4/5 | 0.3802 s |
| `gemini-3.7-flash` | 0/5 | 0/5 | 118.46 MB | 3/5 | 0.3985 s |

All 15 retained executable 96 MB programs were numerically correct and completed
below the disclosed 10-second target. The boundary misses are substantive results:
one Claude and two Gemini programs exceed 96 MB locally despite selecting bounded
implementations. They demonstrate that awareness of a boundary and exact runtime
compliance are separable capabilities.

![Figure 2: Condition-level observed MaxRSS distributions for blind, 128 MB-aware, and independently sampled 96 MB-aware outputs.](../figures/fresh_boundary_sensitivity_maxrss.pdf)

**Figure 2.** Condition-level observed MaxRSS distributions for blind, 128 MB-aware,
and independently sampled 96 MB-aware outputs. Every retained executable result is
shown. The 96 MB series is not paired with the reference series; dashed lines are
observed-RSS classifications, not cgroup enforcement.

### 4.3 Mechanistic interpretation

The source-linked audit covers every included 128 MB script and every retained
executable 96 MB script, with source hashes, line-level evidence, and a predeclared
syntactic classification rule [9]. The two malformed Claude 96 MB responses remain
archived separately and are described in Section 3.3. The audit shows variation in
input mapping, block parameters, precision tokens, temporary-buffer reuse, and
symmetry-related terms. These are observable implementation features, not a claim
that any one feature alone caused a particular RSS value. Together with the
execution measurements, they support the narrower mechanistic conclusion that the
disclosed contract changed resource-relevant generated implementations rather than
uniformly selecting a single canonical algorithm.

## 5. Discussion and Implications

The central finding is that a simple resource contract can alter sampled
computational implementations before they execute. This supports substrate
awareness as a design principle: deployment context can be supplied during planning
instead of being discovered only through runtime enforcement and post-failure retry.

This result does not imply that lower memory is always better. In some serverless
systems, allocating more memory also supplies more CPU and can improve latency [3].
The practical objective is suitability to a known deployment envelope, not blind
minimization of MaxRSS.

The retained Claude blind runtime-compatibility failure is a concrete illustration
of a second kind of substrate-relevant context. Its source used a Python 3.10-style
union annotation that raised a `TypeError` when evaluated by the pinned Python 3.9
runtime [5]. This single incident is not a treatment comparison and does not show
that disclosing a Python version would prevent such errors. It does, however,
illustrate why execution context includes software as well as hardware: an
otherwise plausible program can be unsuitable for the runtime in which it is
deployed. Version-aware generation is therefore a specific future controlled test
of the broader substrate-awareness principle.

The result also does not establish production savings or reliability improvement.
It motivates future end-to-end evaluations in environments with explicit resource
contracts, including containerized workloads, serverless functions, and constrained
devices. It further motivates controlled studies of operational telemetry for tool
selection, recovery, quota handling, and multi-agent routing.

## 6. Limitations and Future Work

This is a controlled numerical-code benchmark, not a universal agent evaluation.
The fresh cohorts are small; the 96 MB samples are independent condition-level
generations; and no causal mechanism inside the models is identified. Measurements
are local observed macOS MaxRSS and wall time, not Linux cgroup survival, CPU quota
behavior, energy, cost, or production incident rates. Model IDs are configured API
identifiers rather than immutable snapshots.

Future work should independently test interpreter/runtime compatibility, CPU quotas
and accelerator availability; GPU/VRAM-aware multimodal pipelines; storage and
network-aware data agents; and telemetry-aware tool use based on latency,
reliability, quota, cost, and remaining context. Each setting requires its own
task-success and operational metrics.

## 7. Reproducibility and Artifact Availability

The repository preserves the direct-API run manifest, prompts hashes, dataset hash,
raw responses, extracted scripts, profiles, and reports for the fresh cohort and
the 96 MB sweep:

- Fresh direct-API analysis and row-level outcomes: `docs/10_direct_api_cohort_analysis.md`.
- Fresh direct-API manifest and harness: `experiments/06_replication/`.
- 96 MB manifest, raw artifacts, and report: `experiments/08_96mb_cgroup_pilot/`.
- Source-linked audit and machine-readable records: `docs/13_fresh_code_transformation_audit.md`
  and `experiments/06_replication/audit/fresh_code_transformation_audit.json`.
- Reproducible vector figures: `benchmarks/render_fresh_cohort_figures.py` and
  `paper/figures/`.
- Deployment-impact source notes: `docs/11_deployment_impact_context.md`.

The generated `.npy` data file is excluded from version control; the final artifact
package must provide and test the documented deterministic data-generation command.

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

[4] A. Verma, L. Pedrosa, M. R. Korupolu, D. Oppenheimer, E. Tune, and J. Wilkes.
Large-scale cluster management at Google with Borg. *Proceedings of EuroSys*, 2015.
https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/.

[5] Project artifact: `experiments/06_replication/RUN_MANIFEST.json` and
`experiments/08_96mb_cgroup_pilot/RUN_MANIFEST.json`.

[6] Project artifact: `experiments/06_replication/run_replication.py`.

[7] Project artifact: `experiments/08_96mb_cgroup_pilot/LOCAL_SWEEP_REPORT.md`.

[8] Project artifact: `docs/10_direct_api_cohort_analysis.md`.

[9] Project artifact: `docs/13_fresh_code_transformation_audit.md` and
`experiments/06_replication/audit/fresh_code_transformation_audit.json`.

## Submission checklist remaining

- Replace the author placeholder with complete, accurate consenting author names
  and affiliations.
- Verify direct provider model IDs/access status and the deterministic
  dataset-generation command in a clean checkout. The generation retry policy is
  documented in Section 3.2.
- Replace project-artifact references with stable repository URLs in the final
  PDF/LaTeX version and verify all bibliography metadata.
- Produce and visually inspect the final PDF/LaTeX source package; keep arXiv title
  and abstract metadata ASCII-safe and the abstract under 1,920 characters.
