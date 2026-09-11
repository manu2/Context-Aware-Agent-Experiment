# AAMAS E0b Calibration and E1 Smoke Report

**Date:** September 11, 2026
**Status:** Passed
**Provider API spend:** $0

## Frozen runtime and assets

- Debian 12, Linux 6.1, CPython 3.11.2.
- NumPy 2.0.2 and Pandas 2.2.3 with transitive versions recorded in the runtime manifest.
- `vectors.npy`: 32,768,128 bytes, SHA-256 `b95a6f21...b9ba9`.
- `transactions.csv`: 3,000,000 rows, 38,333,733 bytes, SHA-256 `26c0b06b...9313b`.

Median process baselines across three runs were 2.9 MB for empty Python, 14.5 MB
after importing NumPy, and 43.5 MB after importing Pandas. Reported peaks include
the interpreter and imports because those bytes consume the target process budget.

## Reference profiles and opposed contracts

| Family | Strategy | Median peak | Median program time |
|---|---|---:|---:|
| Numerical | Eager full matrix | 829.9 MB | 3.19 s |
| Numerical | Bounded rows | 47.4 MB | 5.57 s |
| ETL | Pandas materialization | 284.2 MB | 1.57 s |
| ETL | CSV streaming | 4.4 MB | 5.54 s |

Frozen primary contracts:

| Family | Environment | Memory | Program time | Intended strategy |
|---|---|---:|---:|---|
| Numerical | Memory-tight | 128 MiB | 8.0 s | Bounded |
| Numerical | Latency-tight | 1024 MiB | 4.5 s | Eager |
| ETL | Memory-tight | 128 MiB | 8.0 s | Streaming |
| ETL | Latency-tight | 512 MiB | 3.0 s | Pandas/vectorized |

Across the initial 24 enforced executions, every cell admitted its expected
reference 3/3 and rejected its opposed reference 0/3. Because the first 4.0-second
numerical latency ceiling left less scheduler margin than the other cells, it was
widened before model calls to 4.5 seconds and revalidated: eager passed 5/5 and
bounded passed 0/5. The initial 4.0-second evidence remains archived.

The numerical oracle accepts `TOTAL:` values relative to the float64 blocked
reference (835,795,650.00869) at `rtol=1e-6`, accommodating valid float32 and
reduction-order differences. ETL requires exact parsed integer totals.

## E1 context-isolated smoke

Three context-isolated development responses were imported without editing into
the frozen numerical memory-tight path:

| Condition | Correct/suitable | Peak | Program time |
|---|---|---:|---:|
| P: proactive contract | yes | 23.1 MiB | 1.42 s |
| R: task only | yes | 83.0 MiB | 6.39 s |
| G: generic efficiency | yes | 86.7 MiB | 5.54 s |

This confirms that the pipeline preserves and measures substantive implementation
differences. The responses are development-only and excluded from all empirical
claims. The next gate is the frozen direct-API canary.

## Post-canary amendment

The table above records the original E0b state and is retained as planning
provenance. It is not the current pilot protocol. Worker hardening changed the
observed numerical timings, so the latency-tight numerical ceiling was
recalibrated from 4.5 to 3.0 seconds and passed 5/5 eager versus 0/5 bounded.

Canary v4 then demonstrated that model-generated `csv.reader` streaming was much
faster than the original `DictReader` foil and could satisfy the original ETL
latency envelope. The ETL task was redesigned before the pilot as a conditional
weighted aggregation over the same dataset. Realistic fast references measured
approximately 1.03 s/271 MiB for Pandas and 1.83–2.03 s/4.3 MiB for streaming.
The current ETL contracts are 128 MiB/4.0 s and 512 MiB/1.4 s; each passed 5/5
expected and 0/5 opposed reference executions. The complete amendment trail and
pilot outcome are in [`19_aamas_e2_e3_report.md`](19_aamas_e2_e3_report.md).
