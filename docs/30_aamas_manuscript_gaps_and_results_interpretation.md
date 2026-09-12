# AAMAS manuscript gaps and results-interpretation plan

**Recorded:** 2026-09-12

**Target:** AAMAS 2027 Main Technical Track, Generative and Agentic AI

**Evidence boundary:** frozen 288-trajectory confirmatory cohort plus the separately frozen 82-state matched late-disclosure extension

**Integration status (2026-09-12):** The AAMAS manuscript now includes the full
matrix statement, exact contract table, formal state/timing model, publication
architecture figure, four research questions, one-proactive-versus-two-reactive
comparison, failure and operational-yield table, strategy--suitability table,
token decomposition, matched late-disclosure analysis, structural removal
robustness, expanded contract-centered related work, and an artifact statement.
The 162,901-token workflow difference is reported in context as 25.8% of the
632,269-token late-disclosure workflow, together with the 50-call difference.

## 1. Purpose and editorial stance

This document records the remaining work required to turn the completed AAMAS
study into its strongest conference manuscript. The empirical campaign is
complete. No additional provider trials are required for the claims presently
supported by the paper.

The revision must remain confident and evidence-led. It should state what the
system does, what the experiment establishes, and where the effect appears. It
should not surround supported claims with disclaimers or describe the study as a
prompt-wording exercise. Execution contracts are typed, machine-derived agent
state; P/R/G manipulate when and how that state becomes available in an otherwise
fixed generate--execute--recover architecture.

Post-freeze analyses listed below are secondary or exploratory. They may clarify
mechanism, heterogeneity, and operational consequence, but they must not be
presented as preregistered co-primary tests.

## 2. Current reviewer-style assessment

| AAMAS dimension | Current assessment | Main reason |
|---|---:|---|
| Technical soundness | 9.0/10 | Preregistered balanced design, authentic enforcement, deterministic oracles, randomization inference, retained failures |
| Reproducibility | 9.5/10 | Complete trajectory archive, prompts, programs, execution evidence, manifests, hashes, deterministic analysis and anonymous supplement |
| Empirical strength | 8.5/10 | 288 trajectories across three models, two families, two instances per family, two opposed environments and three conditions |
| Effect strength | 9.0/10 | P first-pass suitability 64/96 versus R 14/96 and G 27/96; both adjusted permutation p-values 1.99998e-05 |
| Originality | 8.0/10 | Concrete treatment of execution contracts as pre-action agent state, compared with reactive discovery and generic intent |
| AAMAS/GAAI fit | 8.5/10 | State/context, runtime infrastructure, agent workflow, recovery, evaluation and assurance |
| Practical significance | 7.5/10 | Large reductions in unsuitable execution, calls and tokens; production deployment remains future validation |
| Agentic contribution | 7.0/10 | Real bounded generate--execute--recover loop, currently under-formalized in the manuscript |
| System depth as presented | 7.0/10 | Reusable adapter/compiler/renderer boundary, but the current boxed-arrow figure undersells it |
| Generality | 6.5/10 | Cross-model and cross-envelope evidence; two deterministic code-generation families on one controlled worker |
| Clarity and presentation | 8.0/10 | Strong narrative and figures; experimental matrix and instance count need clearer presentation |
| Related work | 5.5/10 | Eight references do not yet establish command of the relevant AAMAS and agent-systems literature |

Current posture: credible AAMAS Proceedings candidate and strong Findings
candidate. The largest acceptance risk is perceived architectural thinness or
insufficient differentiation from context wording, not empirical integrity.

## 3. Manuscript gaps to close

### G1. Make the experimental breadth unmistakable

Replace every ambiguous reference to "two task families, two instances" with
"two task families and two independently generated instances per family."

State the full matrix once in prose or notation:

`3 models x 2 families x 2 instances x 2 environments x 3 conditions x 4 repetitions = 288 trajectories`.

### G2. Put the exact environment matrix in the main paper

Add a compact table containing, for each of the four instances:

- task family and instance;
- memory-tight memory and deadline values;
- latency-tight memory and deadline values;
- admitted reference strategy; and
- opposed reference rejected during calibration.

This makes the paper self-contained and lets the reader verify that the
environments test opposing implementation choices.

### G3. Formalize the agent contribution

Add a concise contract schema and state-transition algorithm. The presentation
should identify:

- target inspection and provenance;
- normalized `ExecutionContract` fields and units;
- condition-specific observability before the first action;
- generated program as the agent action;
- kernel-backed execution observation;
- verified suitability decision; and
- the single bounded recovery transition.

Replace the boxed line of arrows with a publication-quality architecture figure.
The figure must visually separate substrate enforcement from substrate-state
projection and show that the executor and scorer remain fixed across P/R/G.

### G4. Expand related work and sharpen differentiation

The revision should cover situated/environment-aware agents, agent state and
context, generative-agent runtimes, resource-aware planning, execution-guided
repair, and efficiency-oriented code benchmarks. The novelty statement should
contrast:

1. correctness-only code evaluation;
2. post-execution feedback and self-repair;
3. generic efficiency prompting; and
4. typed, machine-derived execution state exposed before action selection.

The literature expansion should include relevant AAMAS work, not only general
LLM-agent papers.

### G5. Use the available page budget

The current PDF is five pages. AAMAS permits eight main-content pages. Target
approximately seven to seven-and-a-half substantive pages plus references. Use
the space for G2--G4 and result interpretation, not repetition or defensive
qualification.

### G6. Preserve confident, precise language

Keep statements such as:

> These results establish execution context as consequential agent state.

Replace negative framing such as:

> Execution contracts are therefore not a claim that models never optimize unaided.

with:

> Execution contracts replace model-specific interpretations of efficiency with
> an explicit target objective, producing substantially more consistent
> suitability across providers and opposed execution environments.

Present latency-tight ETL positively as an identified capability boundary. In
the threats section, lead with what the controlled design isolates and then name
the next validation setting.

## 4. Additional findings already supported by the frozen results

### F1. One proactive attempt beats two-attempt alternatives

P produced 64 suitable programs on the first attempt. After their permitted
recovery attempt, R reached only 33 and G reached only 43. Thus the proactive
condition's first attempt exceeded the other conditions' final two-attempt yield
by 31 and 21 trajectories, respectively.

This is one of the strongest agent-level interpretations because it compares
upstream state availability with the completed reactive workflow rather than
with a first attempt alone.

### F2. Reactive failure evidence does not substitute for the execution contract

Initial failures and subsequent recoveries are:

| Condition | Initially unsuitable | Recovered by attempt 2 | Conditional recovery rate |
|---|---:|---:|---:|
| P | 32 | 8 | 25.0% |
| R | 82 | 19 | 23.2% |
| G | 69 | 16 | 23.2% |

The recovery inputs are materially different. P retains the exact RAM, wall-time,
CPU, runtime, and package contract and also receives the execution observation.
R and G receive only the authentic symptom (exit code, timeout flag, OOM-kill
flag, and stdout/stderr tails); the hidden numeric operating limits are not
revealed on attempt 2. Their recovery is therefore inference from failure, not
contract-aware replanning.

The conditional recovery percentages must not be used to compare repair ability:
conditioning on first-attempt failure selects different cases in each condition.
P's residual failures are the cases that remained difficult despite prior
contract disclosure, whereas R and G failures include many avoidable first-pass
mismatches. The primary-matrix result is stronger and simpler: an exact contract
before generation produced 64 suitable first attempts, exceeding the complete
two-attempt yields of R (33) and G (43), even though those conditions could react
to authentic failure evidence. The separately frozen L extension below directly
tests whether revealing the exact contract after failure changes recovery.

This is a descriptive post-freeze analysis and should be labelled accordingly.

#### Completed extension: late contract disclosure

The separately frozen late-disclosure condition (L) reuses every archived
first-attempt R failure as a fixed branch point. The existing R recovery received
the authentic execution observation alone; L received that identical observation
plus the exact RAM, wall-time, CPU, runtime, and package contract. Attempt 1 was
neither regenerated nor re-executed. All 82 branches pass the source, prompt,
artifact, execution, and ledger audit.

Suitable recovery increased from 19/82 under symptom-only feedback to 53/82
under late disclosure. Matched transitions were 35 improvements, one regression,
18 shared successes, and 28 shared failures (descriptive exact McNemar
`p = 1.0768417e-09`). The result replicated with different magnitude across all
three configurations: Gemini 3/27 to 25/27, Claude 8/31 to 13/31, and GPT 8/24
to 15/24. L recovered 18/24 OOM-origin failures and 35/58 timeout-origin failures;
none of the L executions was OOM-killed. Residual failures shifted to 27 timeouts
and two runtime/correctness errors.

This extension strengthens the system result: exact substrate state is actionable
even when supplied after a failure, while proactive disclosure prevents the
failed first action and required 128 provider calls versus 178 for late disclosure.
The strongest agent design exposes the exact contract before planning and retains
contract-aware recovery for residual failures. These findings remain separately
identified from the frozen 288-trajectory P/R/G matrix.

#### Candidate extension: runtime and dependency contracts

The planned compatibility family remains valuable and distinct. It should use
locked containers and two separately controlled subdimensions: interpreter
compatibility (for example, a legacy and a modern CPython environment with the
dependency set held fixed) and dependency-API compatibility (for example,
Pydantic 1.x and 2.x with the interpreter held fixed). This avoids confounding
language-version and library-version effects. The task should exercise meaningful
schema validation and serialization behavior, not a one-line syntax trap. Exact
prompts, images, unit/integration oracles, and API-choice classifications must be
validated before provider calls. The historical Python 3.9 failure motivates this
family but is not counted as its treatment evidence.

### F3. Contracts prevent both memory and time failures

First-attempt failure counts are:

| Condition | OOM kills | Timeouts | Other failure | Total initially unsuitable |
|---|---:|---:|---:|---:|
| P | 2 | 29 | 1 | 32 |
| R | 24 | 58 | 0 | 82 |
| G | 27 | 42 | 0 | 69 |

Relative to R, P reduced first-attempt OOM kills by 91.7% and timeouts by 50.0%.
Relative to G, the reductions were 92.6% and 31.0%. The result is therefore not
only a memory effect.

Across all issued executions, P produced 56 unsuitable runs, versus 145 for R
and 122 for G: reductions of 61.4% and 54.1%.

### F4. The effect is envelope-dependent in an interpretable way

First-pass suitability by environment is:

| Environment | P | R | G |
|---|---:|---:|---:|
| Memory-tight | 46/48 (95.8%) | 13/48 (27.1%) | 21/48 (43.8%) |
| Latency-tight | 18/48 (37.5%) | 1/48 (2.1%) | 6/48 (12.5%) |

The task--environment decomposition is sharper:

| Regime | P | R | G |
|---|---:|---:|---:|
| ETL, memory-tight | 24/24 | 5/24 | 13/24 |
| Numerical, memory-tight | 22/24 | 8/24 | 8/24 |
| Numerical, latency-tight | 17/24 | 0/24 | 5/24 |
| ETL, latency-tight | 1/24 | 1/24 | 1/24 |

This demonstrates two points simultaneously: contract disclosure operates across
memory and latency objectives, and latency-tight ETL exposes a real synthesis
capability boundary shared by all conditions.

### F5. Exact contracts improve cross-model reliability beyond generic intent

P exceeded R for every provider configuration by 46.9--59.4 percentage points.
G was highly configuration-dependent: it approached P for GPT-5.6 Sol but
remained far below P for Claude Sonnet 5 and Gemini 3.8 Flash. The paper should
interpret this as reduced dependence on a model's default meaning of
"efficient," not as a model ranking.

### F6. Broad strategy labels do not fully explain suitability

In the numerical family, both P and G selected blocked computation in 42/48
programs. Yet explicit `float32` retention appeared in 37/48 P programs versus
13/48 G programs. This shows that knowing the target changes lower-level
parameterization even when the broad algorithm family is the same.

In ETL, R frequently selected standard-library streaming (30/48), demonstrating
that a nominally memory-efficient strategy can still be unsuitable for a
latency-tight target. Operational suitability depends on matching strategy and
configuration to the particular envelope, not selecting a universally
"efficient" label.

### F7. The context overhead is repaid in total token use

Token decomposition across all provider calls is:

| Condition | Calls | Input tokens | Output/reasoning tokens | Total tokens |
|---|---:|---:|---:|---:|
| P | 128 | 36,099 | 433,269 | 469,368 |
| R | 178 | 35,076 | 560,626 | 595,702 |
| G | 165 | 37,027 | 634,047 | 671,074 |

Although P carries the explicit contract in its context, its total token use was
21.2% below R and 30.1% below G. The saving comes from fewer calls and fewer
generated output/reasoning tokens, not from pretending that the contract text is
free.

API-dollar differences should not be emphasized: the frozen bootstrap intervals
for estimated cost differences cross zero. Tokens, calls, executions, and
successful-output yield are the stronger provider-independent outcomes.

### F8. Operational yield can be reported descriptively

Calls per final suitable trajectory were 1.78 for P, 5.39 for R, and 3.84 for G.
Total tokens per final suitable trajectory were approximately 6.5k, 18.1k, and
15.6k. These ratios include the cost of unsuccessful trajectories in each fixed
cohort and should be named "cohort-level operational yield," not per-success
latency or an inferential endpoint.

### F9. Suitability is more informative than raw speed alone

P's first program time was 0.218 seconds higher than G's in the stratified
continuous comparison, while P achieved much higher first-pass suitability. At
the final attempt, P and G program times were comparable. This is useful evidence
that optimizing observed runtime in isolation can reward fast but inadmissible
executions; the primary endpoint correctly requires correctness, memory, and time
simultaneously.

## 5. Existing-data analyses and disposition

The high-value analyses below were reviewed for the conference manuscript:

1. **Failure-transition matrix — integrated.** The matched R--L recovery table
   reports OOM- and timeout-origin outcomes, model-level outcomes, and all four
   matched transitions.
2. **Near-miss analysis for latency-tight ETL — retained in the archive.** The
   supervisor terminates timed-out processes at the frozen deadline, so censored
   execution times do not reveal the unobserved completion margin. The paper
   reports the regime as an identified capability boundary without inventing a
   time-to-completion estimate.
3. **Leave-one-model and leave-one-instance sensitivity — integrated.** Recompute the two
   primary risk differences after removing each model and each instance. This
   demonstrates whether the headline result depends on one provider or asset.
4. **Strategy--suitability association — integrated.** Cross-tab frozen strategy features with
   suitability within family and environment. Treat this as descriptive mechanism
   evidence, not proof that a label caused the outcome.
5. **Contract responsiveness versus generic responsiveness — integrated.** Report dispersion
   of condition effects across models and environments, emphasizing exact target
   matching rather than model ranking.
6. **Token decomposition by attempt — integrated.** Separate first-attempt and repair input,
   output, and reasoning tokens to quantify the context cost and avoided recovery
   work cleanly.
7. **CPU and throttling audit — verified as an execution control.** Every frozen
   contract allocates one CPU core and records cgroup CPU statistics. Because CPU
   allocation is held fixed, the manuscript correctly treats it as enforced
   substrate state rather than constructing a separate CPU-treatment claim.

Any new inferential testing must be declared exploratory and receive appropriate
multiplicity handling. Prefer effect sizes, uncertainty intervals, and transparent
counts over a collection of post-hoc p-values.

## 6. Interpretation precedents

- EffiBench separates functional correctness from runtime and memory efficiency
  and shows why pass rate alone is insufficient. Our joint suitability endpoint
  advances the same measurement principle into target-specific agent execution:
  <https://proceedings.neurips.cc/paper_files/paper/2024/hash/15807b6e09d691fe5e96cdecde6d7b80-Abstract-Datasets_and_Benchmarks_Track.html>
- MLAgentBench reports task-level heterogeneity and interpretable plans/actions
  rather than reducing an agent to one aggregate success score. This supports our
  regime and strategy analysis:
  <https://proceedings.mlr.press/v235/huang24y.html>
- Who&When treats failure logs and decisive failure steps as scientific evidence,
  supporting a condition-specific failure taxonomy and recovery-transition view:
  <https://proceedings.mlr.press/v267/zhang25cq.html>
- TIMEARENA evaluates completion, speed, action validity, and behavior under
  resource constraints, supporting joint operational outcomes rather than a
  model leaderboard: <https://openreview.net/pdf?id=BqttonajSN>
- The AAMAS 2027 GAAI call explicitly includes state/context, orchestration,
  runtime infrastructure, failure handling, verification, and benchmarks:
  <https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/>

## 7. Revision order

1. Run the existing-data analyses in Section 5 and freeze a secondary-analysis
   addendum with exact commands and outputs.
2. Expand related work and write the explicit novelty comparison.
3. Add the formal contract schema, state transition, architecture figure, and
   exact environment table.
4. Integrate only the highest-value secondary findings: F1, F2, F3, F6, and F7
   are the leading candidates.
5. Revise tone using G6, rebuild the anonymous PDF, and perform page-by-page
   visual and anonymity review.
6. Re-run the release verifier after inserting the OpenReview submission ID.
