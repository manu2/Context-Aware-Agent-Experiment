# V2 Peer-Review Disposition and Manuscript-Only Revision Plan

**Scope:** This document evaluates the consolidated external review of
`paper_draft_v2.md`. It is an arXiv-preprint review: the standard is a coherent,
scholarly, self-contained proof of concept with correct evidence and citations. It
is not an MLSys acceptance checklist and does not create a requirement for a
production system, a large benchmark suite, or new experiments.

## Bottom line

The review correctly identifies two priorities: the manuscript needs a real related
work/bibliography architecture, and its prose can lead more decisively with the
positive finding. It is wrong to treat local artifact paths as an arXiv moderation
violation, to infer unmeasured performance mechanisms, or to convert source-feature
presence into universal algorithmic transformations.

The next revision is therefore a **manuscript-only** pass. No new trial, cgroup
run, code audit, or benchmark is required.

## Disposition of the empirical and submission claims

| Review recommendation | Verification | Disposition | Planned treatment |
|---|---|---|---|
| Add actual authors, affiliations, and consent | Required for arXiv metadata; anonymous submissions are not accepted. | Valid; user-owned | Insert only after the authors provide accurate, consenting information. |
| Replace local-path artifact references | Local paths are poor public bibliography entries and must become stable release URLs in the final public paper. However, arXiv accepts ancillary files and does not publish a rule that internal paths automatically trigger moderation flags. | Valid editorial fix; incorrect stated rationale | Move artifact paths out of References into Artifact Availability; link a tagged GitHub release in the final TeX/PDF. |
| Add ReAct, SWE-bench, Toolformer, Green AI, and serverless papers | ReAct, SWE-bench, and Toolformer are real relevant agent/code-agent context. Green AI is real but this paper does not measure energy/cost. Serverless resource-characterization work supports the deployment-contract motivation. | Partially valid | Add only citations that support text actually present: ReAct and SWE-bench for agent/code-agent context; a serverless resource-management characterization for deployment context. Do not pad the bibliography with Toolformer or Green AI unless a corresponding substantive discussion sentence is retained. |
| Replace defensive language | v2 contains a few unnecessary minimizers: “one small piece,” “deliberately simple,” and “artificial threshold.” The experiment itself is not weak. | Valid | Replace with positive, precise language; retain only measurement/scope qualifiers that prevent a false claim. |
| Lead with the dual memory/time outcome | Raw results verify lower mean wall time for every cohort: Claude 0.9109 -> 0.3612 s (2.52x), GPT 0.5507 -> 0.3282 s (1.68x), Gemini 1.0994 -> 0.3561 s (3.09x). Mean MaxRSS reductions are approximately 58%, 46%, and 65%, respectively. | Valid descriptive result | Put the dual outcome in Abstract/Results/Discussion as an observed joint outcome of the disclosed-contract condition. Do not claim the prompt caused cache locality, prevented GC churn, or eliminated thrashing; none was profiled. |
| Present four universal structural transformations | The source audit finds named blocking in 14/15 blind and 13/15 disclosed 128 MB scripts; explicit `out=` in 15/15 of both; symmetry-related terms in 8/15 of both; and `mmap_mode` in 8/15 of both. | Invalid as written | Do not describe these as universal transitions caused by disclosure. Use a small number of paired case studies to show how resource-relevant choices changed (for example block size, precision promotion, traversal, or input handling), while the complete audit supplies the corpus-level evidence. |
| Explain GPT `rep04` as NumPy-buffer variance | The run records one RSS regression, 65.70 -> 87.64 MB. No buffer-allocation mechanism was measured. | Unsupported | Report it neutrally as a model-dependent regression; do not explain its cause. |
| Use Python 3.9 failure as a software-substrate example | The archived stderr establishes a Python 3.9 runtime compatibility failure from evaluating a Python 3.10-style union annotation. It is not a version-disclosure treatment. | Valid with current v2 framing | Retain as a concrete illustration of the broader information gap, with one concise sentence distinguishing it from the RAM/time controlled test. |

## What the source audit actually supports

The strongest accurate mechanism claim is:

> Across the fresh cohort, disclosed resource context changed the distribution of
> resource-relevant implementation choices, including block sizing, precision
> handling, traversal extent, temporary-buffer strategy, and input mapping. The
> source corpus does not support a claim that every blind program was eager or that
> every disclosed program adopted the same optimization.

This wording owns the observation while respecting the code. The task's dense
8,000-by-8,000 float32 distance intermediate is 256 MB, but the fresh blind corpus
already contains many blocked implementations. Therefore, “all models transformed
eager O(N^2) code into streaming code” would be false.

## Model-family comparison: do not add a Flash-versus-reasoning claim

The Gemini 3.7 Flash cohort has the largest observed absolute mean MaxRSS drop in
this experiment (452.36 -> 158.16 MB) and lower observed RSS in all five executable
pairs. That is a valid cohort description.

It is not evidence that “Flash models are more substrate-aware than deep-thinking
models.” The study has no comparable internal reasoning traces or standardized
reasoning-effort variable; provider configurations differ; each cohort contains only
five pairs on one task; and no model-family population was sampled. The manuscript
should continue to say **model-dependent responsiveness**. A future study could
explicitly manipulate reasoning mode or planning budget with matched models/tasks.

## Proposed v3 manuscript pass

1. **Opening and abstract:** retain the v2 title and broad thesis. Replace
   diminutive phrasing with “pre-execution disclosure of an operational envelope.”
   Lead with 13/14 paired reductions and the observed dual memory/time outcome.
2. **Related work:** add a concise section, not a citation dump. Position this work
   next to agent action/planning and execution-grounded code-agent evaluation, then
   distinguish it: the intervention is *pre-execution environment information*,
   not tool-use feedback or post-failure repair.
3. **Results:** preserve both tables and figures. Add one sentence with the three
   observed speedup ratios; retain GPT `rep04` as a neutral regression. Replace any
   “not merely” rhetoric with direct description of the audited implementation
   variation.
4. **Mechanism discussion:** use two or three source-linked paired examples, not a
   forced taxonomy of four universal transformations. The table-wide audit remains
   the evidence of coverage.
5. **Discussion and scope:** lead with the positive principle--planning should be
   conditioned on its operating contract. Put exact scope in one compact paragraph
   near the end; do not hedge every result sentence.
6. **Artifacts and references:** move project artifacts to a GitHub release link in
   Artifact Availability. Reserve References for scholarly work and standards.
7. **Final production, after content approval:** author block, stable release tag,
   TeX/PDF conversion, citation and render check. These are submission production
   tasks, not empirical gaps.

## Verification sources consulted

- arXiv submission guidance: authors and abstracts are required; arXiv accepts
  ancillary data/program files but does not require them.
- ReAct, SWE-bench, and Toolformer primary papers were verified as real. They are
  candidates only when their relationship to the paper is explicitly written.
- `experiments/06_replication/audit/fresh_code_transformation_audit.json` and raw
  profile metadata were used to check the mechanism and speedup recommendations.
