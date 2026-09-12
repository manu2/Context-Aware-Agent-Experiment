# AAMAS 2027 OpenReview checklist

This is an author-side registration aid. It is not included in the anonymous
supplement.

## Venue and area

- Venue: AAMAS 2027 Main Technical Track
- Primary area: Generative and Agentic AI (GAAI)
- Paper type: Research Paper Track
- Abstract deadline: 2026-10-01, Anywhere on Earth
- Paper deadline: 2026-10-08, Anywhere on Earth

GAAI is the direct fit: the contribution concerns state/context architecture,
runtime support, generate-execute-recover behavior, failure handling, and
evaluation of generative agents. EMAS is a plausible secondary area but should
not replace GAAI because the empirical object is the generative agent's planning
behavior.

## Copy-ready metadata

**Title**

Execution Contracts as Agent State: Proactive Substrate Awareness for Autonomous
Code Generation

**Abstract**

Autonomous coding agents choose implementations whose suitability depends on the
target environment, yet the model may select a plan before the environment's
memory and time boundaries enter its planning state. We study execution contracts
as first-class agent state: compact, machine-derived descriptions of the resources
that determine whether an implementation is admissible. We present an Execution
Contract Bridge that inspects a target, compiles its effective contract, and
controls when that state becomes visible in an autonomous generate-execute-recover
loop. Our preregistered evaluation compares proactive contract disclosure with
reactive execution feedback and generic efficiency guidance across three model
configurations, two task families, two instances, and opposed memory- and
latency-tight Linux environments. Across 288 independently generated trajectories,
proactive disclosure produced 64/96 (66.7%) first-pass suitable programs, compared
with 14/96 (14.6%) under reactive feedback and 27/96 (28.1%) under generic
efficiency guidance. Equal-stratum risk differences were +52.1 and +38.5
percentage points, respectively (both Holm-adjusted permutation p = 2.0 x 10^-5).
We then branch from all 82 reactive first-attempt failures while holding the failed
program and authentic observation fixed. Adding the exact contract to recovery
raises suitable repairs from 19/82 to 53/82, with 35 matched improvements and one
regression (exact McNemar p = 1.08 x 10^-9). Removal analyses preserve both primary
advantages after excluding any model, instance, task family, environment type, or
individual stratum. These results establish execution context as consequential,
persistent agent state: proactive disclosure prevents unsuitable first actions,
and exact state at recovery transforms the agent's ability to repair the same
failures.

**Keywords**

autonomous agents; coding agents; context engineering; resource-aware planning;
execution contracts; empirical evaluation

## Author and policy fields

- Add the real author through the existing OpenReview profile. Author identities
  are visible to chairs but must not appear in the review PDF or supplement.
- Affiliation: use the affiliation approved for this independent work; do not add
  an employer affiliation without that employer's publication approval.
- Prior preprint: answer accurately if the form asks. AAMAS permits prior
  non-archival arXiv preprints. The manuscript cites the precursor neutrally in
  the third person and never labels it as the authors' own work. The confidential
  field additionally states the relationship and the substantive research delta.
- Reciprocal reviewer: designate the author only if the AAMAS reviewer eligibility
  criteria are met. Otherwise select the published exemption that no author is
  qualified and complete the requested exemption declaration.
- Generative-AI use: answer yes if asked and use the concise disclosure in
  `AI_ASSISTANCE_DISCLOSURE.md`. The author remains fully responsible for all
  content and validation.
- Findings consideration: leave enabled unless the author intentionally wants to
  opt out of an archival Findings publication if the paper is not selected for
  the main proceedings.

## Confidential prior-preprint disclosure

If OpenReview provides a prior-work or confidential-comments field, enter:

> Related non-archival preprint: Manu Agrawal, “Substrate-Aware AI Agents:
> Execution Context as a First-Class Input,” arXiv:2609.05232 (2026). The present
> submission is a substantial extension: it introduces the Execution Contract
> Bridge and an autonomous generate-execute-recover architecture; executes under
> Linux cgroup enforcement; expands to two task families, two independent
> instances, and opposed memory/latency environments; reports a preregistered
> 288-trajectory P/R/G evaluation and an 82-state matched late-disclosure recovery
> extension; and adds workflow, strategy, and removal-robustness analyses. The
> preprint's earlier single-task macOS study is non-archival and is not under
> simultaneous archival review.

Keep this disclosure in the chair-visible submission field. The anonymous PDF
contains an ordinary third-person citation to the precursor, without identifying
it as the authors' work; the confidential disclosure makes the relationship and
research delta explicit to the chairs. This follows the current AAMAS reviewer
guidance that guessability from citations or prior work is not itself an anonymity
violation unless the submission explicitly reveals author identity.

## Upload sequence

1. Register title, abstract, authors, area, keywords, conflicts, and reciprocal
   reviewer/exemption by the abstract deadline.
2. Copy the assigned submission ID into `\acmSubmissionID{...}`.
3. Rebuild the PDF and anonymous supplement.
4. Run the release verifier and require zero failures.
5. Upload `main.pdf` and `aamas2027_anonymous_supplement.zip`.
6. Inspect the OpenReview-rendered PDF and supplement download before finalizing.

Official sources:

- <https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/>
- <https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/reciprocal-reviewer-policy/>
- <https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/reviewer-guidelines/>
