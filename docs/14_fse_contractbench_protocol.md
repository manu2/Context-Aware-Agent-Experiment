# ContractBench: FSE Expansion Protocol

**Status:** planned; no provider generation is authorized by this document.
**Target:** ACM FSE 2027 Research Track.
**Relationship to the arXiv manuscript:** a new, expanded study. The current
numerical proof of concept remains a separately identifiable preprint and is not
silently pooled with this protocol's results.

## 1. Research objective

This study evaluates whether a code-generation system produces software that is
more suitable for its target deployment environment when it receives a truthful
operational contract before generation.

An operational contract is a versioned, machine-verifiable description of the
facts that determine suitability for a particular execution environment. It can
include resource limits, interpreter and dependency versions, filesystem policy,
input scale, timeout, and permitted output locations. It never prescribes an
algorithm, a library, a datatype, a block size, or a repair strategy.

The primary question is:

> Across distinct software tasks, does an execution contract improve the rate of
> correct first-pass executions that satisfy the stated environment?

The study investigates generated-program selection and observable execution
outcomes. It does not infer an internal model representation or claim provider-
wide rankings.

## 2. Contribution and evidence boundary

The intended FSE contribution is **ContractBench**, a reproducible benchmark and
execution-contract interface for evaluating generated software under deployment
facts that materially affect implementation suitability.

The paper will distinguish this from generic non-functional-requirement prompting:

- each contract field is collected from, or verified against, the exact target
  environment that runs the generated program;
- each task has an external correctness oracle and an enforced environment;
- source, prompt, contract, environment manifest, execution trace, and analysis
  record are retained for every generation;
- the benchmark covers resource, runtime/dependency, and deployment-policy
  dimensions rather than one numerical workload.

## 3. Benchmark architecture

```text
versioned task spec + target environment
                 |
                 v
contract collector ---> normalized manifest ---> prompt renderer
                 |                                  |
                 +---------------> archive <--------+
                                                    |
                                                    v
provider response --> source extraction --> isolated execution --> evaluator
                                                    |
                                                    v
                              raw trace, cgroup events, metrics, classifications
```

The collector is read-only. It produces a manifest from the target container,
not from a separately maintained prompt file. The manifest schema records both
values and collection provenance, for example:

```json
{
  "schema_version": "contractbench-v1",
  "runtime": {"python": "3.11.9", "packages": {"pydantic": "1.10.18"}},
  "resources": {"memory_max_bytes": 100663296, "cpu_quota": "100000 100000"},
  "execution": {"wall_timeout_s": 10, "network": "disabled"},
  "filesystem": {"root_read_only": true, "writable_outputs": ["/output"]}
}
```

Only fields relevant to the current task are rendered into a condition prompt.

## 4. Core task families

### T1. Bounded numerical computation

**Task:** compute a specified pairwise-distance result from a deterministic
float32 array and write the required output.

**Contract dimension:** cgroup memory limit and wall-time budget.

**Expected observable choices:** blocking/tiling, precision retention, symmetry
exploitation, and temporary-buffer reuse versus eager quadratic materialization.

**Evaluator:** a fixed reference implementation validates numerical output with
predeclared tolerance. The runner records cgroup limit events, peak memory, exit
status, elapsed time, and output hash.

### T2. Large-file streaming transformation

**Task:** transform a deterministic CSV or JSONL input into a required aggregate
or output artifact (for example, grouped statistics plus top-k records).

**Contract dimension:** input scale, cgroup memory limit, output location, and
the availability of a writable temporary/output path.

**Expected observable choices:** bounded chunk processing, incremental output,
and bounded aggregation state versus full-file materialization.

**Evaluator:** generate data locally from a checked-in seed and specification;
compare the output artifact with an oracle; record limit events, peak memory,
output correctness, elapsed time, and temporary-file usage. No multi-gigabyte
dataset is committed to Git.

### T3. Runtime and dependency compatibility

**Task:** implement a small schema-validation or serialization CLI against a
fixed input/output contract.

**Contract dimension:** exact Python and dependency version. The initial
candidate is a versioned Pydantic environment, where the target API differs
between supported versions.

**Expected observable choices:** compatible API and import selection, fallback
logic where appropriate, and syntax valid for the stated interpreter.

**Evaluator:** execute unit and integration tests in locked container images.
The outcome includes import success, test pass rate, error type, and source-level
API classification.

**Selection rule:** every compatibility instance must be based on official
runtime/library documentation, must be solved correctly in every declared target
environment, and must be hand-validated before any model call. A one-line syntax
trap is not an acceptable standalone instance.

### Optional pilot: read-only filesystem

A separate pilot may use a read-only root filesystem with a declared `/output`
mount. It is promoted to a fourth family only if blind and contract conditions
show a distinct, reproducible implementation difference. It is not part of the
core launch matrix.

## 5. Information conditions

The primary comparison is task-only generation versus a structured contract
generated by the collector. Natural-language disclosure establishes whether the
benefit is available through a human-readable representation as well.

| ID | Condition | Prompt content |
|---|---|---|
| A | Task-only | Functional specification and output requirements only. |
| B | Neutral-context control | Task-only prompt plus length-matched, decision-irrelevant operational prose. Used on a representative subset. |
| C | Natural-language contract | Task prompt plus a factual, algorithm-neutral textual rendering of the target contract. |
| D | Structured contract | Task prompt plus the collector's normalized JSON/key-value manifest. |

All prompt templates, field ordering, output-format requirements, and renderer
versions are frozen before provider calls. Natural-language templates are tested
for semantic equivalence during the design stage; the full study uses one
predeclared template unless a template-sensitivity sub-study is explicitly added.

## 6. Context-isolated design gate (before provider spending)

Before any real API campaign, each task must pass an independent, zero-project-
context review. The reviewer receives only the candidate task prompt, contract,
container manifest, evaluator specification, and acceptance criteria; it receives
none of the current paper, prior results, expected strategy, or desired outcome.

The review has four outputs:

1. Identify facts leaked by the task prompt that make the hidden contract obvious.
2. Identify whether the disclosed contract accidentally supplies an algorithmic
   recipe or a named solution.
3. Propose at least two plausible implementations that are functionally correct
   but differ in operational suitability.
4. Attempt to defeat the evaluator with a superficially compliant or degenerate
   program.

The task owner then revises the task/evaluator and records the review in
`contractbench/design_reviews/`. The reviewer is not asked to estimate results or
to author trial code. This gate validates task separability and information
hygiene; it is not experimental evidence.

## 7. Preflight and calibration

Each task/environment instance must satisfy all of the following before it enters
the manifest:

- A hand-written unsuitable implementation is functionally correct but violates
  the contract under the exact container.
- A hand-written suitable implementation is functionally correct and satisfies
  the contract with margin.
- The contract collector exactly matches the running container's runtime,
  filesystem, resource, and policy facts.
- The evaluator rejects wrong, partial, stale-output, and fake-output programs.
- The task prompt does not disclose the contract through file names, comments,
  package listings, error transcripts, or requested algorithmic terminology.
- A positive control demonstrates that the cgroup memory limit and timeout are
  active; cgroup `memory.events`, `memory.peak`, exit status, and timeout status
  are retained.

Calibration records are archived and limits are frozen before the first provider
call. Thresholds cannot be adjusted after observing provider generations.

## 8. Sampling plan and progression

Provider outputs are independent stochastic generations unless a provider offers
and honors a documented shared seed. Identically numbered blind and contract
trials are organizational identifiers, not a basis for paired-inference tests.

### Stage 0: no-cost design and implementation

Build containers, collector, prompt renderer, data generator, external oracle,
positive controls, and context-isolated design reviews. No provider request is
made in this stage.

### Stage 1: pilot

One configured model; three task families; two predeclared environment instances
per family; A/C/D conditions; three independent generations per cell.

`3 tasks x 2 instances x 3 conditions x 3 generations = 54` provider
generations.

Advance a task family only when it has a meaningful blind mismatch opportunity,
clean enforcement, no information leak, and a valid evaluator. Failed task design
is a reason to replace the task, not to weaken the evaluator or reinterpret the
outcome.

### Stage 2: main benchmark

The default full matrix is A/D for all cells, with C and B used as representation
and length controls on a predeclared subset:

- A/D core: `3 tasks x 2 instances x 3 model configurations x 2 conditions x
  8 generations = 288` generations.
- C/B subset: one instance per task, all three model configurations:
  `3 tasks x 3 models x 2 added conditions x 8 generations = 144` generations.
- **Planned maximum: 432 generations.**

The matrix may not be reduced after results are visible. If the budget cannot
support it, select a smaller matrix before the campaign, document it, and do not
describe it as the full benchmark.

### Stage 3: optional trajectory companion

Only after Stage 2, select a predeclared subset and compare blind one-shot,
blind-plus-execution-feedback, and contract-aware one-shot behavior with a fixed
retry cap. Measure first-pass success, attempts, tool calls, tokens, and total
execution footprint. This is a companion study, not a prerequisite for FSE.

## 9. Execution and artifact rules

- Call order is randomized/interleaved across task, instance, condition, and
  model configuration.
- Each generation receives a unique immutable trial ID reserved before the API
  request. Failed transport attempts and malformed outputs remain recorded.
- Every trial archives the exact request body, raw provider response, source
  extraction result, prompt hash, model configuration, SDK version, timestamp,
  environment manifest hash, container digest, evaluator version, stdout/stderr,
  cgroup events, measurements, and correctness result.
- Fresh working directories and containers prevent output, cache, and temporary
  state from leaking between trials.
- Executions are rerun only according to a predeclared measurement policy. Such
  reruns estimate runtime variation; they never become additional generation
  observations.
- All results, including malformed output, syntax errors, wrong output, timeout,
  and contract violations, remain in the denominator for applicable outcomes.

## 10. Outcomes and analysis

**Primary outcome:** correct first-pass execution that satisfies the declared
operational contract.

**Secondary outcomes:** correctness, contract-violation category, cgroup memory
events, `memory.peak`, elapsed time, output hash, source-level implementation
taxonomy, and (only in Stage 3) retries, tool calls, tokens, and total completion
footprint.

Analysis is generated from row-level records. It will report counts and confidence
intervals by task family, environment instance, condition, and named model
configuration; raw observations and within-task normalized resource/time changes;
and predeclared source labels. Bootstrap uncertainty or a model that respects the
task/model structure is preferred to tests that assume independently generated
conditions are matched pairs. The analysis plan will name one primary contrast
(A versus D) before the main campaign.

## 11. Source-level taxonomy

The classification rubric is frozen before Stage 2. Labels include:

- bounded/blockwise numerical processing;
- precision and temporary-buffer management;
- streaming/incremental input or output;
- bounded-state aggregation;
- runtime-compatible syntax/API/import selection;
- environment-policy-compliant path or temporary-file choice;
- no relevant adaptation / unsuitable implementation.

Automated AST or token rules provide initial labels. Ambiguous cases receive a
blinded manual audit by a reviewer who cannot see the condition label.

## 12. FSE-ready reproducibility and disclosure

From the first pilot onward, maintain an anonymizable replication package with:

- task specs, deterministic data generators, container definitions, and image
  digests;
- collector and prompt-renderer source;
- evaluator/oracle source and positive-control logs;
- run manifest, raw trial artifacts, analysis code, and generated tables/figures;
- exact descriptions of model use, human review, and any AI assistance that
  materially contributed to methods, artifacts, analyses, or figures.

Before submission, generate a heavy-double-anonymous package and a Data
Availability statement. The package must not reveal author identity, local paths,
private credentials, or a submission destination.

## 13. Decision gates

| Gate | Decision question | Required result |
|---|---|---|
| G0: design | Are task and contract information cleanly separable? | Context-isolated review completed; no algorithm leakage. |
| G1: calibration | Does the actual environment distinguish suitable and unsuitable hand-written implementations? | Both positive and negative controls pass. |
| G2: pilot | Does each retained family yield valid, interpretable trial artifacts? | Evaluator/enforcement work and blind mismatch is plausible. |
| G3: scale | Is the frozen matrix affordable and technically stable? | Budget, storage, containers, provider configuration, and analysis are locked. |
| G4: submission | Does the paper make a distinct multi-environment contribution beyond the arXiv proof of concept? | Complete evidence package, anonymous artifact, and claim audit. |

## 14. Explicit non-goals

- This protocol does not rank model providers or model tiers.
- This protocol does not claim a guarantee of compliance from contract disclosure.
- This protocol does not substitute a retry-loop study for the primary
  first-pass experiment.
- This protocol does not pool historical, proxy, or current arXiv cohorts into
  its main analysis.
- This protocol does not make an MLSys runtime-system claim; its automatic
  collector is an FSE benchmark interface and a possible future foundation.
