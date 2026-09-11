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
