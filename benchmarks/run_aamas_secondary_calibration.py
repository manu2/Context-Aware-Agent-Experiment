#!/usr/bin/env python3
"""Model-free calibration for the second frozen instance in each task family."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aether_contract_bridge.compiler import ContractCompiler
from aether_contract_bridge.execution import SSHLinuxExecutionBackend
from aether_contract_bridge.models import RawSubstrateEvidence


PROGRAMS = {
    "numerical_eager": """import numpy as np
x = np.load('vectors_secondary.npy')
norms = np.sum(x * x, axis=1, dtype=np.float32)
d2 = norms[:, None] + norms[None, :] - 2.0 * (x @ x.T)
np.maximum(d2, 0.0, out=d2)
np.sqrt(d2, out=d2)
print(f'TOTAL:{np.sum(d2, dtype=np.float64):.6f}')
""",
    "numerical_bounded": """import numpy as np
x = np.load('vectors_secondary.npy', mmap_mode='r')
norms = np.sum(x * x, axis=1, dtype=np.float32)
total = 0.0
block = 256
for start in range(0, x.shape[0], block):
    rows = np.asarray(x[start:start + block])
    d2 = rows @ x.T
    d2 *= -2.0
    d2 += norms[start:start + block, None]
    d2 += norms[None, :]
    np.maximum(d2, 0.0, out=d2)
    np.sqrt(d2, out=d2)
    total += float(np.sum(d2, dtype=np.float64))
print(f'TOTAL:{total:.6f}')
""",
    "etl_dataframe": """import json
import pandas as pd
df = pd.read_csv('transactions_secondary.csv', usecols=['account_id', 'category', 'amount_cents'])
mask = (df['account_id'] % 13) < 8
selected = df.loc[mask, ['account_id', 'category', 'amount_cents']]
weighted = selected['amount_cents'] * ((selected['account_id'] % 89) + 3)
result = weighted.groupby(selected['category'], sort=True).sum()
print('TOTAL:' + json.dumps({str(k): int(v) for k, v in result.items()}, sort_keys=True, separators=(',', ':')))
""",
    "etl_streaming": """import csv
import json
totals = {}
with open('transactions_secondary.csv', newline='') as handle:
    reader = csv.reader(handle)
    header = next(reader)
    account_i, category_i, amount_i = (header.index(name) for name in ('account_id', 'category', 'amount_cents'))
    for row in reader:
        account = int(row[account_i])
        if account % 13 < 8:
            key = row[category_i]
            totals[key] = totals.get(key, 0) + int(row[amount_i]) * ((account % 89) + 3)
print('TOTAL:' + json.dumps(totals, sort_keys=True, separators=(',', ':')))
""",
}

ENVELOPES = {
    "numerical_memory_tight": {"memory_mib": 128, "wall_seconds": 8.0,
                                "expected": "numerical_bounded", "opposed": "numerical_eager"},
    "numerical_latency_tight": {"memory_mib": 1024, "wall_seconds": 3.0,
                                 "expected": "numerical_eager", "opposed": "numerical_bounded"},
    "etl_memory_tight": {"memory_mib": 128, "wall_seconds": 4.0,
                          "expected": "etl_streaming", "opposed": "etl_dataframe"},
    "etl_latency_tight": {"memory_mib": 512, "wall_seconds": 1.4,
                           "expected": "etl_dataframe", "opposed": "etl_streaming"},
}


def contract(memory_mib: int, wall_seconds: float):
    return ContractCompiler().compile(RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1", target_id="gcp-secondary-calibration",
        observed_at_utc=datetime.now(timezone.utc).isoformat(), source="model-free-reference",
        memory_max_bytes=memory_mib * 1024 * 1024, cpu_quota_cores=1,
        wall_time_limit_seconds=wall_seconds, runtime="CPython 3.11.2",
        packages=("numpy==2.0.2", "pandas==2.2.3"),
    ))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"),
                        required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--repetitions", type=int, default=5)
    args = parser.parse_args()
    common = dict(host=args.host, user="manuagrawal",
                  identity_file=Path.home() / ".ssh/google_compute_engine",
                  worker_local_path=ROOT / "benchmarks/aether_execution_worker.py")
    backends = {
        "numerical": SSHLinuxExecutionBackend(**common, assets={"vectors_secondary.npy": "/opt/aether-data/vectors_secondary.npy"}),
        "etl": SSHLinuxExecutionBackend(**common, assets={"transactions_secondary.csv": "/opt/aether-data/transactions_secondary.csv"}),
    }
    records = []
    for envelope_name, envelope in ENVELOPES.items():
        family = envelope_name.split("_", 1)[0]
        for role in ("expected", "opposed"):
            strategy = envelope[role]
            for repetition in range(1, args.repetitions + 1):
                observation = backends[family].run(
                    PROGRAMS[strategy], contract(envelope["memory_mib"], envelope["wall_seconds"])
                )
                records.append({"envelope": envelope_name, "role": role, "strategy": strategy,
                                "repetition": repetition, "observation": observation.to_dict()})
    outputs = {}
    for family in ("numerical", "etl"):
        values = {r["observation"]["stdout"].strip() for r in records
                  if r["strategy"].startswith(family) and r["observation"]["exit_code"] == 0}
        if family == "numerical":
            parsed = [float(value.removeprefix("TOTAL:")) for value in values]
            if not parsed or (max(parsed) - min(parsed)) / max(abs(v) for v in parsed) > 1e-6:
                raise RuntimeError(f"numerical references disagree: {values}")
            outputs[family] = {"values": sorted(values), "oracle_value": statistics.mean(parsed),
                               "relative_tolerance": 1e-6, "absolute_tolerance": 1e-3}
        else:
            if len(values) != 1:
                raise RuntimeError(f"ETL references disagree: {values}")
            outputs[family] = {"value": values.pop(), "comparison": "exact parsed JSON integer mapping"}
    checks = {}
    summaries = {}
    for envelope_name, envelope in ENVELOPES.items():
        subset = [r for r in records if r["envelope"] == envelope_name]
        summaries[envelope_name] = {}
        for role in ("expected", "opposed"):
            observations = [r["observation"] for r in subset if r["role"] == role]
            passes = [o["exit_code"] == 0 and not o["timed_out"] and not o["oom_killed"] for o in observations]
            summaries[envelope_name][role] = {
                "passes": sum(passes), "n": len(passes),
                "program_seconds": [o["program_time_seconds"] for o in observations],
                "memory_peak_mib": [None if o["memory_peak_bytes"] is None else o["memory_peak_bytes"] / 1048576 for o in observations],
            }
        checks[envelope_name] = (summaries[envelope_name]["expected"]["passes"] == args.repetitions and
                                 summaries[envelope_name]["opposed"]["passes"] == 0)
    payload = {
        "schema_version": "aamas-secondary-calibration/v0.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repetitions": args.repetitions,
        "passed": all(checks.values()), "checks": checks, "reference_outputs": outputs,
        "summary": summaries, "records": records,
    }
    output = ROOT / "experiments/09_aamas_contract_bridge/calibration/e4_secondary_instance_calibration.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "passed": payload["passed"], "checks": checks,
                      "reference_outputs": outputs}, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
