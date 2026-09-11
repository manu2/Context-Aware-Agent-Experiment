# AAMAS 2027 submission readiness

**Evidence freeze:** 2026-09-12  
**Target:** Main Technical Track, Generative and Agentic AI (GAAI)  
**Official deadlines:** abstract 2026-10-01; paper 2026-10-08, Anywhere on Earth  
**Status:** empirical and technical package complete; release metadata pending

## Requirement-to-evidence audit

| Requirement | Authoritative evidence | Status |
|---|---|---|
| Reusable generate-execute-recover path | `src/aether_contract_bridge/`; `tests/test_contract_bridge.py` | Passed |
| Authentic Linux cgroup v2 memory, CPU, timeout, and offline controls | `docs/17_aamas_e0a_report.md`; calibration archive | Passed |
| Frozen tasks, environments, runtime, oracles, manifests, models, attempt policy, and source hashes | `docs/22_aamas_e4_protocol_freeze.md`; `experiments/09_aamas_contract_bridge/protocol/` | Passed before confirmatory generation |
| Cost-controlled smoke, canary, and non-pooled pilot | `docs/18_aamas_e0b_e1_report.md`; `docs/19_aamas_e2_e3_report.md`; API ledgers | Passed |
| Complete confirmatory matrix | Three complete provider audits; `docs/26_aamas_confirmatory_completion_gate.md` | 288/288 effective trajectories |
| Outcome-neutral infrastructure recovery | `docs/23_aamas_e5_infrastructure_interruption.md`; `docs/27_aamas_gpt_infrastructure_interruption.md` | Preserved and audited |
| Frozen confirmatory analysis | `experiments/09_aamas_contract_bridge/analysis/confirmatory_analysis.json`; `docs/28_aamas_confirmatory_results.md` | Reproduces deterministically |
| Anonymous AAMAS manuscript | `paper/aamas2027/main.tex`; locally generated `main.pdf` | Five pages; verifier passes |
| Anonymous reproducibility supplement | `benchmarks/build_aamas_supplement.py`; local `paper/aamas2027/aamas2027_anonymous_supplement.zip` | 3.43 MB; deterministic; verifier passes |
| Tests and release checks | `tests/test_contract_bridge.py`; `tests/test_aamas_submission.py`; `benchmarks/verify_aamas_submission.py` | 15/15 tests pass |

## Frozen headline evidence

Proactive contract disclosure produced 64/96 first-pass suitable trajectories,
compared with 14/96 for reactive feedback and 27/96 for generic efficiency
guidance. Equal-stratum improvements are +52.1 and +38.5 percentage points;
both Holm-adjusted randomization p-values are 1.99998e-05. The result reproduces
across all three provider-configured models and three of four task-environment
regimes. Latency-tight ETL is the retained boundary case.

## Anonymous supplement record

- Filename: `aamas2027_anonymous_supplement.zip`
- Members: 2,967
- Effective trajectories declared: 288
- Archived trajectory slots: 320, including 32 preserved pre-generation Gemini
  quota-interruption slots
- Size: 3,432,057 bytes
- SHA-256: `db181f1c92ca2862b88c6fb50da21beaf64dd5cd6245b0c724ab535fe231cef3`
- Provider transport envelopes are omitted; exact textual generations, programs,
  prompts, execution records, summaries, analyses, and hashes are retained.
- Local worker identifiers are normalized only in packaged copies; the manifest
  records original and packaged hashes for every transformed member.

## Final release sequence

1. Register the anonymous abstract in OpenReview and record the assigned
   submission ID.
2. Replace `\acmSubmissionID{PENDING}` in `paper/aamas2027/main.tex` with that ID.
3. Rebuild `main.pdf` and `aamas2027_anonymous_supplement.zip`.
4. Run:

   ```bash
   .venv/bin/python3 benchmarks/verify_aamas_submission.py \
     --release --pdf paper/aamas2027/main.pdf
   ```

5. Upload the verified PDF and optional anonymous supplement. Select GAAI. Do not
   cite or link the public arXiv preprint or public repository in the anonymous
   submission.

## Remaining release controls

- **OpenReview submission ID:** not yet assigned; this is the only current
  fail-closed verifier error.
- **Public Git synchronization:** local `main` contains the raw GPT archive and
  final documentation/supplement tooling commits. Publishing those provider
  responses requires the repository owner's explicit approval.

The official AAMAS 2027 call permits prior non-archival preprints, requires a
double-blind submission, and evaluates originality, significance, soundness,
reproducibility, clarity, relevance, presentation, and command of related work:
<https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/>.
