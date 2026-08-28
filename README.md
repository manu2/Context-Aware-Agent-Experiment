# Substrate-Aware AI Agents

This repository contains a controlled proof of concept for **substrate
awareness**: giving an AI agent decision-relevant execution context before it
selects an implementation. It tests the broader planning proposition through an
inspectable pathway--numerical code generation conditioned on a RAM/time contract.

An agent's task says what to do; execution context helps determine which plan is
suitable in the environment where the action will run. Memory, time, compute
availability, runtime versions, tool reliability, quota, and cost are examples.
The evaluated intervention supplies RAM/time context and records the resulting
code, numerical output, MaxRSS, and wall time.

## Primary evidence: fresh direct-API cohort

The primary cohort is 15 predeclared, fresh direct-API A/D pairs: five pairs each
for configured provider model IDs `claude-opus-5`, `gpt-5.6-sol`, and
`gemini-3.7-flash`. The conditions differ only in whether the code-generation
prompt discloses a 128 MB RAM and 10-second wall-time contract. It supplies no
algorithmic recipe and performs no execution-feedback repair before measurement.

| Configured model ID | Executable A/D comparisons with lower disclosed MaxRSS | Mean MaxRSS, blind -> disclosed | Correct / observed `<=128 MB`, blind -> disclosed |
|---|---:|---:|---:|
| `claude-opus-5` | 4/4 | 256.48 -> 107.82 MB | 0/5 -> 5/5 |
| `gpt-5.6-sol` | 4/5 | 118.63 -> 64.61 MB | 4/5 -> 5/5 |
| `gemini-3.7-flash` | 5/5 | 452.36 -> 158.16 MB | 0/5 -> 2/5 |

One retained Claude blind script fails under the pinned Python 3.9 runtime and is
therefore retained in correctness denominators but excluded from Claude's
continuous blind mean and paired MaxRSS direction. The GPT cohort contains one
RSS regression; the Gemini disclosed outputs exceed the observed 128 MB boundary
in three of five trials. These are results, not omissions.

All primary MaxRSS values are isolated local macOS process observations. The
threshold columns report correct executions whose observed process peak falls within
the disclosed RAM envelope.

## What the study establishes

The evidence establishes a controlled, model-dependent proof of concept: a
pre-execution resource contract changed the sampled generated implementations,
lowered observed MaxRSS in 13 of 14 executable 128 MB comparisons, and lowered
mean wall time in every model cohort. The source-linked audit identifies concrete
resource-relevant choices--input mapping, block parameters, data types, traversal,
and temporary-buffer reuse--rather than a universal switch to one algorithm.

The manuscript develops the broader substrate-awareness agenda, including runtime
compatibility, accelerators, tools, quota, reliability, and cost, as the next
settings for this planning intervention.

## Reproduction and audit

```bash
# One-time setup.
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt

# Create the deterministic numerical input and check its hash.
.venv/bin/python3 data/generate_dataset.py
shasum -a 256 data/vectors.npy

# Rebuild the source-linked JSON and Markdown audit (no API calls).
.venv/bin/python3 benchmarks/build_fresh_code_audit.py --overwrite

# Re-render the final paper figures from archived metadata (no API calls).
.venv/bin/python3 benchmarks/render_final_paper_figures.py

# Verify the fresh-cohort raw artifacts, audit digests, and figures.
.venv/bin/python3 benchmarks/verify_fresh_evidence_package.py
```

For local manuscript review, add `--manuscript path/to/draft.md`; this additionally
checks the draft's displayed result rows and required measurement-language clauses.

The expected SHA-256 for `data/vectors.npy` is
`199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085`.

The live API harness is in `experiments/06_replication/run_replication.py`. It
atomically reserves each trial directory, archives terminal artifacts, and permits
up to three API transport attempts inside a trial. Do not reuse a trial ID or
overwrite raw artifacts. Provider-facing model IDs are recorded configurations,
not immutable model-weight snapshots.

## Artifact guide

- [Canonical manuscript](paper_draft.md): the locally prepared arXiv manuscript,
  including its author block, verified tables, and final figures. It presents the
  broad substrate-awareness thesis through a controlled numerical-code-generation
  proof of concept and remains under author/affiliation clearance.
- [Manuscript figures](paper/figures/): reproducible vector PDFs used by the
  canonical manuscript. The final TeX package will include them with
  `\\includegraphics`.
- [Internal review PDF](paper/review/substrate_aware_ai_agents_v6_review.pdf):
  the rendered review copy prepared for author and affiliation clearance.
- [Paper archive](paper/archive/): superseded drafts, figures, and rendered review
  copies retained for revision provenance rather than publication use.
- [Direct-API cohort analysis](docs/10_direct_api_cohort_analysis.md): complete fresh 128 MB row-level outcomes.
- [Generated-code audit](docs/13_fresh_code_transformation_audit.md): all retained fresh sources, with a machine-readable [JSON companion](experiments/06_replication/audit/fresh_code_transformation_audit.json).
- [96 MB local sweep report](experiments/08_96mb_cgroup_pilot/LOCAL_SWEEP_REPORT.md): separately sampled condition-level boundary-sensitivity extension.
- [Execution tracker](EXECUTION_TRACKER.md): live execution history and provenance notes.

Historical exploratory and earlier canonical artifacts remain preserved under
`experiments/` and `docs/`. They are not silently pooled with the fresh direct-API
cohort because their provenance and protocol precede the frozen direct-API design.
`benchmarks/run_peer_reviewer.py` is retained solely as a historical checker for
the old canonical draft; it is not evidence validation for the working revision.

## Submission status

The manuscript is locally complete and undergoing author/affiliation clearance; it
is not an arXiv upload package yet. Before any submission, obtain clearance,
convert the approved source to TeX/PDF, include the figures, and perform a final
independent evidence/claim audit. arXiv itself does not require this JSON audit or
code review; those are voluntary reproducibility measures for this empirical
preprint. A decision to release source code and raw artifacts remains separate.
