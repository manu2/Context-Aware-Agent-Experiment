#!/usr/bin/env python3
"""Profile the post-canary ETL redesign using realistic fast references."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
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
    "pandas": """import json
import pandas as pd
df = pd.read_csv('transactions.csv', usecols=['account_id', 'category', 'amount_cents'])
mask = (df['account_id'] % 11) < 7
selected = df.loc[mask, ['account_id', 'category', 'amount_cents']]
weighted = selected['amount_cents'] * ((selected['account_id'] % 97) + 1)
result = weighted.groupby(selected['category'], sort=True).sum()
print('TOTAL:' + json.dumps({str(k): int(v) for k, v in result.items()}, sort_keys=True, separators=(',', ':')))
""",
    "streaming": """import csv
import json
totals = {}
with open('transactions.csv', newline='') as handle:
    reader = csv.reader(handle)
    header = next(reader)
    account_i, category_i, amount_i = (header.index(name) for name in ('account_id', 'category', 'amount_cents'))
    for row in reader:
        account = int(row[account_i])
        if account % 11 < 7:
            category = row[category_i]
            totals[category] = totals.get(category, 0) + int(row[amount_i]) * ((account % 97) + 1)
print('TOTAL:' + json.dumps(totals, sort_keys=True, separators=(',', ':')))
""",
}


def contract():
    return ContractCompiler().compile(RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1",
        target_id="gcp-e0b-etl-redesign",
        observed_at_utc=datetime.now(timezone.utc).isoformat(),
        source="post-canary-model-free-reference",
        memory_max_bytes=1024 * 1024 * 1024,
        cpu_quota_cores=1,
        wall_time_limit_seconds=20,
        runtime="CPython 3.11.2",
        packages=("numpy==2.0.2", "pandas==2.2.3"),
    ))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"),
                        required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--repetitions", type=int, default=5)
    args = parser.parse_args()
    backend = SSHLinuxExecutionBackend(
        host=args.host, user="manuagrawal",
        identity_file=Path.home() / ".ssh" / "google_compute_engine",
        worker_local_path=ROOT / "benchmarks" / "aether_execution_worker.py",
        assets={"transactions.csv": "/opt/aether-data/transactions.csv"},
    )
    records = []
    for name, program in PROGRAMS.items():
        for repetition in range(1, args.repetitions + 1):
            observation = backend.run(program, contract())
            records.append({"strategy": name, "repetition": repetition,
                            "observation": observation.to_dict()})
            if observation.exit_code != 0:
                raise RuntimeError(f"{name} repetition {repetition} failed")
    outputs = {r["observation"]["stdout"].strip() for r in records}
    if len(outputs) != 1:
        raise RuntimeError(f"reference outputs disagree: {outputs}")
    summary = {}
    for name in PROGRAMS:
        observations = [r["observation"] for r in records if r["strategy"] == name]
        summary[name] = {
            "n": len(observations),
            "memory_peak_mib": [o["memory_peak_bytes"] / (1024 * 1024) for o in observations],
            "memory_peak_median_mib": statistics.median(o["memory_peak_bytes"] / (1024 * 1024) for o in observations),
            "program_time_seconds": [o["program_time_seconds"] for o in observations],
            "program_time_median_seconds": statistics.median(o["program_time_seconds"] for o in observations),
        }
    payload = {
        "schema_version": "e0b-etl-redesign-candidate/v0.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "reason": "Canary v4 showed that optimized csv.reader streaming satisfied the original latency-tight envelope; the original DictReader foil was not representative.",
        "candidate_task": "Conditional weighted aggregation by category using account_id and amount_cents.",
        "reference_output": outputs.pop(),
        "summary": summary,
        "records": records,
    }
    output = ROOT / "experiments/09_aamas_contract_bridge/calibration/e0b_etl_redesign_candidate_profiles.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
