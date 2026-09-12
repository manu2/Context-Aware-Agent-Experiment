# AAMAS Execution Contract Bridge Study

This directory contains the new autonomous generate–execute–recover study. All
outputs under `development_smoke/` are development-only and excluded from paper
results. Empirical cohorts remain separated under the directories declared in
the research plan.

The E0a vertical slice uses the same contract, rendering, execution, scoring, and
archive interfaces intended for the direct-API canary and main campaign. It has
passed an imported-response trajectory on the dedicated Debian 12 worker plus
fail-closed cgroup v2 memory-kill and timeout controls.

Run local interface tests:

```bash
python3 -m unittest discover -s tests -v
```

With the declared GCP worker running, deploy and run the zero-cost fixture:

```bash
python3 benchmarks/run_aamas_e0a_fixture.py --host WORKER_IP --deploy-worker
python3 benchmarks/run_aamas_e0a_controls.py --host WORKER_IP
```

## Frozen late-disclosure recovery extension

The completed extension branches from all 82 archived condition-R first-attempt
failures. Each L recovery receives the archived execution observation plus the
exact target contract; the original 288-trajectory P/R/G matrix is unchanged.

- Versioned manifests: `protocol/late_disclosure_*_v1.json`
- Complete raw branches and append-only ledgers: `late_disclosure/`
- Provider audits: `analysis/*_late_disclosure_v1.json`
- Cross-model audit: `analysis/late_disclosure_combined_v1.json`
- Combined report: `../../docs/34_aamas_late_disclosure_combined_report.md`

Rebuild and verify the derived analyses:

```bash
python3 benchmarks/analyze_aamas_late_disclosure.py --manifest late_disclosure_gemini38_v1.json --analysis experiments/09_aamas_contract_bridge/analysis/gemini_late_disclosure_v1.json --report docs/31_aamas_gemini_late_disclosure_report.md
python3 benchmarks/analyze_aamas_late_disclosure.py --manifest late_disclosure_anthropic_sonnet_v1.json --analysis experiments/09_aamas_contract_bridge/analysis/claude_late_disclosure_v1.json --report docs/32_aamas_claude_late_disclosure_report.md
python3 benchmarks/analyze_aamas_late_disclosure.py --manifest late_disclosure_openai_sol_v1.json --analysis experiments/09_aamas_contract_bridge/analysis/gpt_late_disclosure_v1.json --report docs/33_aamas_gpt_late_disclosure_report.md
python3 benchmarks/analyze_aamas_late_disclosure_combined.py
```
