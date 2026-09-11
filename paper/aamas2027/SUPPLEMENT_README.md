# Anonymous AAMAS 2027 supplementary artifact

This archive accompanies the anonymous manuscript **Execution Contracts as Agent
State: Proactive Substrate Awareness for Autonomous Code Generation**. It contains
the frozen protocol, reusable Execution Contract Bridge implementation, exact
experimental prompts and generated programs, execution-derived summaries, and the
  deterministic confirmatory analysis for all 288 effective trajectories. The
  archive also preserves 32 original pre-generation Gemini quota-interruption
  slots so the outcome-neutral replacement ledger can be audited.

## What is included

- `src/aether_contract_bridge/`: contract compilation, rendering, provider,
  execution, scoring, recording, and agent-loop implementation;
- `benchmarks/`: calibration, execution, audit, analysis, and figure-generation
  entry points used by the study;
- `experiments/09_aamas_contract_bridge/protocol/`: frozen manifests, task and
  environment definitions, source hashes, and analysis plan;
- `experiments/09_aamas_contract_bridge/confirmatory/`: exact prompts, raw textual
  generations, extracted programs, execution events, trajectory manifests,
  strategy labels, and summaries for the confirmatory cohort;
- `experiments/09_aamas_contract_bridge/analysis/`: complete cohort audits and the
  machine-readable confirmatory analysis;
- `docs/`: protocol-freeze, interruption, completion-gate, strategy-codebook, and
  generated result reports;
- `manifest.json`: SHA-256 digest and byte size for every other archive member.

Provider transport envelopes are deliberately omitted: they contain operational
request identifiers but no scientific evidence beyond the included raw textual
generation and recorded usage fields. Generated datasets are also omitted because
the frozen generators and hashes recreate them deterministically.

For double-blind review, the builder normalizes the collection host's local worker
account literal in packaged text files. `manifest.json` records both the frozen
source hash and the packaged hash for every file and flags each transformed member.
No task, prompt, model response, generated program, metric, outcome, or analysis
value is changed.

## Reproduce the analysis

From the extracted archive root:

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt
.venv/bin/python3 benchmarks/analyze_aamas_confirmatory.py
.venv/bin/python3 benchmarks/generate_aamas_figures.py
.venv/bin/python3 -m unittest tests.test_contract_bridge
```

The analysis is offline and makes no provider calls. Authentic cgroup execution
requires Linux with cgroup v2 and the dependencies documented in the frozen
protocol. The archived execution records are sufficient to reproduce every table,
statistical comparison, and figure in the manuscript without rerunning models.
