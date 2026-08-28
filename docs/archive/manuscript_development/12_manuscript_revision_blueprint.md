# Manuscript Revision Blueprint: Substrate-Aware AI Agents

**Status:** Revision plan only. It does not modify `paper_draft.md` or reinterpret
raw artifacts. It records the agreed narrative hierarchy: a broad agentic thesis,
a rigorous code-generation proof of concept, and explicitly prospective extensions.

## 1. Narrative hierarchy

### Thesis (broad)

Execution context is decision-relevant information for AI agents. An agent that
knows the task but not the environment in which it must act is *substrate-blind*:
its plan is not deliberately conditioned on memory, time, CPU/GPU availability,
tool reliability, quota, cost, or other operational constraints.

### Evidence in this paper (specific)

This paper evaluates one first instance of that thesis: zero-shot,
pre-execution disclosure of a RAM/time contract during numerical code generation.
The task is deliberately narrow because generated code, numerical correctness,
process MaxRSS, and wall time can all be inspected independently.

### Future research program (prospective)

The paper should motivate, but not claim to have demonstrated, other dimensions:
CPU/GPU/VRAM-aware planning; storage and network-aware data agents; telemetry-aware
tool selection and recovery; token/cost-aware multi-agent routing; and
resource-conditioned multimodal pipelines.

## 2. Evidence map

| Status | Artifacts | Manuscript role |
|---|---|---|
| **Primary evidence** | `docs/10_direct_api_cohort_analysis.md`; `experiments/06_replication/RUN_MANIFEST.json`; per-trial direct-API artifacts | Fresh 128 MB paired replication: 15 included A/D pairs across Claude, GPT, and Gemini. |
| **Primary supporting evidence** | `experiments/08_96mb_cgroup_pilot/LOCAL_SWEEP_REPORT.md`; v1.5 manifest and raw profiles | Separate 96 MB condition-level boundary sensitivity; not matched triples and not pooled with the 128 MB pairs. |
| **Mechanistic evidence to catalogue** | Fresh generated scripts in `experiments/06_replication/raw/` and `experiments/08_96mb_cgroup_pilot/raw/` | Code-level differences: bounded blocks, symmetry, precision, mapping, and in-place temporaries. Create a row-complete audit table before manuscript editing. |
| **Context / motivation** | `docs/11_deployment_impact_context.md` | Kubernetes, serverless, managed containers, and device constraints motivate the thesis; no production-savings claim. |
| **Historical corroboration only** | `docs/01`–`06`; `experiments/05_paired_statistical_trials/` | Preserve and label as historical/exploratory. Do not pool with fresh direct-API evidence. The Phase 2 JSON/prose conflict bars aggregate use until reconciled. |
| **Pilot / audit records** | `docs/07_*`; `docs/08_rigorous_peer_review_audit.md` | Reproducibility history and lessons learned; do not use as main empirical tables. |

## 3. Recommended paper identity

**Recommended title:**

> **Substrate-Aware AI Agents: Execution Context as a First-Class Input to Computational Planning**

**Abstract opening:**

> AI agents typically receive a task specification without the physical and
> operational context in which their actions will execute. We call this omission
> substrate blindness. We investigate whether a simple pre-execution resource
> contract can change an agent's computational planning, using numerical code
> generation as an inspectable proof of concept.

**Headline result:**

> In fresh direct-API paired trials, RAM/time disclosure commonly changed
> resource-relevant generated implementations and lowered observed MaxRSS and mean
> wall time. The size and reliability of this effect varied by model and boundary.

Avoid universal language such as “all agents,” “eliminates failures,” “guaranteed,”
or “proves the mechanism.” Ambition belongs in the thesis and implications; the
quantitative claims belong to the measured code-generation setting.

## 4. Proposed manuscript structure

1. **Introduction — the broad idea.** Define substrate blindness as an
   informational condition. Establish that deployment platforms already expose
   CPU/memory/time contracts, then state the narrow empirical question.
2. **Conceptual framework.** Describe execution context as a possible agent input.
   Show the tested RAM/time instance and diagram untested future dimensions as
   future work, not components evaluated here.
3. **Methods.** Specify task, exact prompt conditions, direct provider IDs and
   sampling configurations, dataset/prompt hashes, isolated local profiling,
   correctness oracle, and provenance rules. Separate observed MaxRSS from cgroup
   enforcement.
4. **Results I — fresh paired 128 MB replication.** Make this the main table.
   Report all outcomes, including the Claude runtime-compatibility failure, GPT regression, and
   Gemini's incomplete threshold compliance.
5. **Results II — 96 MB boundary sensitivity.** Report independent condition-level
   distributions, not matched trajectories. Include all three model cohorts and
   malformed-response handling.
6. **Mechanisms.** Present a complete code-transformation audit, then a few
   illustrative code excerpts.
7. **Discussion and implications.** Explain pre-execution conditioning as a
   complement to runtime enforcement and retry. Discuss cloud/container relevance
   without claiming measured dollars or production incident reduction.
8. **Limitations and future work.** Keep broad SCAC dimensions here.

## 5. Tables and figures

| Item | Content | Required caution |
|---|---|---|
| Table 1 | Fresh direct-API A/D cohort: RSS, wall time, correctness, observed `<=128 MB` | “15 included pairs”; Claude continuous blind mean excludes its non-executable script. |
| Figure 1 | Paired MaxRSS slope plot, one panel per model | Use only executable pairs for continuous lines; visibly mark the Claude runtime-compatibility failure. |
| Table 2 | 96 MB condition-level blind-reference / 128-aware-reference / 96-aware distributions | No pooled test; no matched-triple or cgroup-survival wording. |
| Figure 2 | Per-model condition distribution plot with 96 and 128 reference lines | Present variability and threshold misses, not only means. |
| Table 3 | Complete code-transformation audit | Do not imply every blind script was eager or every aware script adopted a wholly new algorithm. |
| Appendix | Historical cohorts and the four-condition exploratory screen | Clearly label provenance and known Phase 2 inconsistency. |

## 6. Claims to make

- The intervention is **zero-shot and pre-execution**: it gives a deployment
  contract before code selection, without fine-tuning or an execution-feedback
  correction loop.
- It changes **resource-relevant implementation choices**, not merely text output.
- In this benchmark it preserves numerical correctness in all 15 retained 96 MB
  programs and is associated with lower mean observed wall time in all three fresh
  128 MB model cohorts.
- Constraint awareness and exact boundary compliance are separable: some programs
  use bounded strategies yet exceed the observed 96 MB reference because of runtime
  and temporary-allocation overhead.
- The result motivates **deployment-conditioned agent planning** across additional
  operational dimensions.

## 7. Claims to avoid

- “CPU-aware” or “CPU-quota adaptation”: the prompt disclosed a wall-time target,
  not a CPU quota or core allocation.
- “Pareto-optimal,” “guaranteed,” “eliminates,” “all agents,” or production-cost
  savings.
- Cgroup survival based on macOS observed MaxRSS.
- A causal effect of the 10-second clause alone; the fresh cohort does not isolate
  RAM-only from RAM-plus-time prompting.
- Pooling historical, proxy/subagent, exploratory, fresh, or 96 MB samples.

## 8. Required pre-edit checks

1. Create and verify the complete code-transformation audit table from every
   fresh direct script, using artifact links and a transparent classification rule.
2. Verify exact provider-facing model identifiers, API endpoints, dates, sampling
   configurations, and access status; put this information in Methods and the
   artifact appendix.
3. Repair bibliography metadata and ensure each related-work citation supports the
   sentence it is attached to.
4. Exclude the unresolved historical Phase 2 aggregate from the main manuscript.
5. Render the revised manuscript and rerun the numerical/provenance audit before
   submission.

## 9. Open-item closure tracker

“Evidence sufficient” means the completed repository artifacts are enough to close
the item without new experimental generations. It does not mean the final manuscript
already contains the required wording or figure.

| Item | Repository evidence | What is unavailable | Status | Closure action |
|---|---|---|---|---|
| Broad thesis and evidence boundary | Fresh direct-API/96 MB reports plus `docs/09` and `docs/11` | General effects in tool use, multimodal systems, or production | Evidence sufficient | Use the exact Introduction, Discussion, and Future Work text in §10. |
| Fresh results in paper | `docs/10` and `LOCAL_SWEEP_REPORT.md` contain every displayed value | Nothing | Evidence sufficient | Replace historical-first results with the planned tables and figures. |
| Code-transformation claim | Raw responses, scripts, and profiles exist for all fresh direct/retained 96 MB programs | A row-complete verified classification | **Closed:** 45-record source-linked audit generated | `docs/13_fresh_code_transformation_audit.md` and `experiments/06_replication/audit/fresh_code_transformation_audit.json`. |
| Correctness, RSS, and time | Profile artifacts, correctness oracle, environment fingerprint, deterministic data | Real cgroup outcomes for local cohorts | Evidence sufficient; wording pending | State local observed MaxRSS/wall time; retain cgroup pilot separately. |
| Provider identity | Configured API IDs, endpoints, policies, timestamps, prompt/dataset hashes, raw output | Immutable model snapshots and provider request IDs | Partially sufficient | Call IDs configured provider IDs and state snapshot limitation. |
| Retry accounting | Source allows up to three retries; terminal failure records are retained | Per-attempt history for successful calls | Partially sufficient | State allowed policy; do not claim exactly one request per response. |
| Dataset reproduction | `data/generate_dataset.py` seed 42 and SHA assertion; rerun verified SHA | Nothing material | Evidence sufficient | Add exact command/SHA to Methods, README, and artifact appendix. |
| Bibliography | Authoritative records found for every identified correction | Nothing material | **Partially closed:** production-context references corrected in working revision | Final TeX package should use stable repository URLs for project artifacts. |
| Statistical presentation | All row-level values and failures retained | Large-sample population estimate | Evidence sufficient for descriptive reporting | Show all points/failures; no pooled p-value. |
| Figures/PDF source | JSON/profile values sufficient for plots | Publication rendering | **Partially closed:** checked-in renderer and two visually inspected PDF figures | Add final TeX/PDF manuscript render after authorship is supplied. |
| Authorship | Nothing may be inferred from artifacts | Accurate consenting author/affiliation data | User-owned blocker | User supplies final names/affiliations. |
| Historical material | Preserved but Phase 2 aggregate conflict documented | Reconciled Phase 2 aggregate | Insufficient for aggregate use | Appendix/supporting context only; do not quote unresolved aggregate. |

## 10. Copy-ready manuscript and documentation changes

### A. Complete code-transformation audit

**Conclusion:** Existing data is sufficient. The raw corpus supports a complete
audit; no new generation is needed. The audit must distinguish a source-visible
fact from an interpretation of its likely performance effect.

**New artifact to create:** `docs/13_fresh_code_transformation_audit.md` and a
machine-readable companion JSON. Each included fresh A/D script must receive an
artifact-linked row with executability/correctness, input mode (`load`/`mmap`),
matrix precision, pairwise-materialization shape, symmetry use, temporary-buffer
discipline, declared block values, MaxRSS, wall time, and threshold status. The
non-executable Claude blind row remains present. A deterministic extractor may list
candidate features, but a human verifies every classification against `script.py`.

**Exact manuscript addition, Results—Mechanisms:**

> We audited every included fresh script using source-visible implementation
> features: input mapping, precision, pairwise-materialization shape, symmetry,
> temporary-buffer handling, and declared block parameters. The disclosed condition
> does not uniformly replace one algorithm with another. Instead, it shifts
> resource-relevant implementation choices, including block shape, precision,
> traversal extent, and temporary allocation discipline. The complete row-level
> audit and linked scripts are available in the artifact repository.

### B. Provider configuration and retry policy

**Conclusion:** Existing artifacts conclusively support configured-ID reporting.
They cannot retroactively recover provider snapshots, response IDs, or successful
call retry histories. This is a disclosure issue, not an experimental rerun issue.

**Exact manuscript addition, Methods—Generation and provenance:**

> We report the provider-facing model identifiers configured in the frozen
> manifests, together with endpoint, sampling configuration, timestamp, prompt
> hash, and dataset hash. These identifiers describe the provider API configuration
> used for the archived calls; the study does not claim access to immutable provider
> weight snapshots or provider request identifiers. The generation client permitted
> up to three retries after provider errors. Per-attempt request logs were not
> retained, so a retained response is treated as the terminal output of the
> configured generation procedure rather than evidence of exactly one provider
> request.

**Exact manuscript addition, Limitations:**

> Provider-hosted model aliases and service behavior can change over time. The
> archived raw responses and configured API metadata support artifact-level
> reproducibility, but they do not freeze an independently redistributable model
> snapshot.

### C. Dataset and local measurement reproduction

**Conclusion:** Fully resolvable from existing artifacts. This command was rerun on
2026-08-27 and produced the recorded hash.

```bash
.venv/bin/python3 data/generate_dataset.py
shasum -a 256 data/vectors.npy
# expected: 199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085
```

**Exact manuscript addition, Methods—Input data:**

> The 8,000 by 1,024 float32 input is generated deterministically with NumPy seed
> 42. The generation script asserts SHA-256
> `199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085`; the same
> hash is checked before generation and profiling.

**Exact manuscript addition, Artifact availability:**

> From a clean checkout, run `python3 data/generate_dataset.py` before profiling.
> The expected SHA-256 is
> `199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085`.

### D. Measurement semantics and time result

**Conclusion:** Fully resolvable from profiler/environment artifacts. Do not
describe the time target as a CPU quota or local observed RSS as cgroup survival.

**Exact manuscript addition, Methods—Measurement:**

> Each generated script was executed in an isolated local subprocess on macOS 15.5
> arm64 with Python 3.9.6 and NumPy 2.0.2. BLAS-related thread environment variables
> were pinned to one thread. We recorded wall time and
> `resource.getrusage(RUSAGE_CHILDREN).ru_maxrss` after the generated-script child
> exited, converting Darwin's byte-valued result to MB. A 60-second watchdog
> prevented hangs; the 10-second value was a disclosed target scored from observed
> wall time, not an OS-enforced CPU quota.

**Exact manuscript addition, Results—Time:**

> Across the three fresh model cohorts, the jointly disclosed 128 MB and 10-second
> condition had lower mean observed wall time as well as lower observed MaxRSS.
> Because the two clauses were jointly disclosed, this association does not isolate
> the causal contribution of the time clause or demonstrate CPU-quota adaptation.

### E. Statistics and figures

**Conclusion:** Fully resolvable from existing row-level profiles. The right
response to small N is transparent visualization, not a pooled cross-cohort test.

**New checked-in outputs:** a data-extraction script reading raw metadata/profile
JSON; Figure 1 paired MaxRSS slope plots (one panel/model, Claude runtime-compatibility failure
marked); Figure 2 separate blind/128/96 point distributions with threshold lines.

**Exact Figure 1 caption:**

> **Observed memory in fresh direct-API paired trials.** Each line connects one
> blind and jointly disclosed 128 MB/10-second generation for the same predeclared
> pair. Points are isolated local-process MaxRSS measurements, not cgroup outcomes.
> The Claude blind runtime-compatibility failure is shown as a non-executable outcome rather than
> omitted from the experiment.

**Exact Figure 2 caption:**

> **Condition-level boundary sensitivity.** Points show correct, exit-zero local
> programs from separately sampled blind-reference, 128 MB-aware-reference, and
> 96 MB-aware conditions. The 96 MB-aware samples are not matched continuations of
> the 128 MB samples. Horizontal lines are observed-MaxRSS reference boundaries,
> not kernel-enforced cgroup limits.

### F. Bibliography and production-context citations

**Conclusion:** Fully resolvable editorially from authoritative sources. Correct
ActPlane to arXiv:2606.25189 (2026); AgentSight to its PACMI@SOSP 2025 record;
RLEF to Gehring et al. and its ICML 2025 publication; and SafeCodeRL to *Sensors*
26(11), article 3502 (2026). Add Kubernetes, Cloud Run, AWS Lambda, and Borg only
to bounded production-context statements.

**Exact manuscript addition, Introduction—Motivation:**

> Deployment systems already expose resource contracts: Kubernetes schedules work
> from declared requests and enforces limits, while managed-container and
> serverless platforms bind runtime behavior and billing to resource configuration.
> These systems motivate the question studied here; they are not themselves an
> evaluation environment in this paper.

### G. Historical reports, README, and final source package

**Conclusion:** No new experiment needed. Preserve older reports but ensure they
cannot be mistaken for primary fresh evidence.

**Required repository changes after manuscript approval:**

1. Update README to lead with the broad thesis and fresh direct-API/96 MB reports;
   move historical tables below that entry point.
2. Replace `paper_draft.md` only after this working revision has figures, code audit,
   bibliography, authorship, and render check.
3. Convert the accepted Markdown to a checked-in LaTeX/PDF source package and
   visually inspect every page, table, figure, link, and reference.

**Exact manuscript addition, Artifact availability:**

> The repository preserves frozen manifests, prompt and dataset hashes, configured
> provider metadata, raw responses, extracted scripts, isolated-process profiles,
> and the analysis code used for each displayed result. Historical and exploratory
> artifacts are retained for provenance but are not pooled with the fresh direct-API
> cohorts.

## 11. Residual items after all repository-based fixes

Only two facts remain inherently unavailable from the completed experiment:

1. immutable provider model snapshots/request IDs and per-attempt retry histories;
2. final author identity, affiliation, and submission consent.

Neither requires new experimental runs. The first is resolved as a transparent
limitation; the second requires the submitting authors. Every other tracked item
can be fully closed with the existing repository plus ordinary analysis and
manuscript-production work.
