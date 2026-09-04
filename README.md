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

The primary cohort is 15 predeclared, fresh direct-API task-only and
contract-disclosed generations: five per condition for configured provider model
IDs `claude-opus-5`, `gpt-5.6-sol`, and `gemini-3.7-flash`. Identically numbered
A/D calls are traceability identifiers, not statistically matched generations. The
conditions differ only in whether the code-generation
prompt discloses a 128 MB RAM and 10-second wall-time contract. It supplies no
algorithmic recipe and performs no execution-feedback repair before measurement.

| Configured model ID | Index-aligned comparisons with lower disclosed MaxRSS | Mean MaxRSS, task-only -> disclosed | Correct / observed `<128 MiB`, task-only -> disclosed |
|---|---:|---:|---:|
| `claude-opus-5` | 4/4 | 256.48 -> 107.82 MiB | 0/5 -> 5/5 |
| `gpt-5.6-sol` | 4/5 | 118.63 -> 64.61 MiB | 4/5 -> 5/5 |
| `gemini-3.7-flash` | 5/5 | 452.36 -> 158.16 MiB | 0/5 -> 2/5 |

One retained Claude blind script fails under the pinned Python 3.9 runtime and is
therefore retained in correctness denominators but excluded from Claude's
continuous task-only mean and index-aligned MaxRSS comparison. The GPT cohort contains one
RSS regression; the Gemini disclosed outputs exceed the observed 128 MB boundary
in three of five trials. These are results, not omissions.

All primary MaxRSS values are isolated local macOS process observations, reported
in MiB (`bytes / 2^20`). The task text retains its literal `128 MB` label; the
archived primary scorer uses a strict `<128 MiB` observed threshold.

## What the study establishes

The evidence establishes a controlled, model-dependent proof of concept: a
pre-execution resource contract changed the sampled generated implementations,
lowered observed MaxRSS in 13 of 14 executable index-aligned 128 MB comparisons, and lowered
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
  canonical manuscript. These reproducible vector PDFs are the figures used by the
  manuscript and can be regenerated locally.
- Author-review PDF: The manuscript source and reproducible vector figures are
  versioned in this repository. The author-review PDF is intentionally a local
  build artifact; generate it with `python3 benchmarks/render_preprint_review_pdf.py`.
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

The repository contains the finalized manuscript source, vector figures, and
evidence-verification tooling. The public artifact accompanies the arXiv
preprint; the archival submission PDF is generated locally from the
manuscript source. arXiv itself does not require this JSON audit or code review;
those are voluntary reproducibility measures for this empirical preprint. The
repository is prepared to be made public with the preprint release.
