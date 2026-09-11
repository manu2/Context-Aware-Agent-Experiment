#!/usr/bin/env python3
"""Model-free E0b calibration for runtime baselines and primary task references."""

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
    "baseline_empty": "pass\n",
    "baseline_numpy": "import numpy as np\nprint(np.__version__)\n",
    "baseline_pandas": "import pandas as pd\nprint(pd.__version__)\n",
    "numerical_eager": """import numpy as np
x = np.load('vectors.npy')
norms = np.sum(x * x, axis=1, dtype=np.float32)
d2 = norms[:, None] + norms[None, :] - 2.0 * (x @ x.T)
np.maximum(d2, 0.0, out=d2)
np.sqrt(d2, out=d2)
print(f'TOTAL:{np.sum(d2, dtype=np.float64):.6f}')
""",
    "numerical_bounded": """import numpy as np
x = np.load('vectors.npy', mmap_mode='r')
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
    "etl_pandas": """import json
import pandas as pd
df = pd.read_csv('transactions.csv', usecols=['account_id', 'category', 'amount_cents'])
mask = (df['account_id'] % 11) < 7
selected = df.loc[mask, ['account_id', 'category', 'amount_cents']]
weighted = selected['amount_cents'] * ((selected['account_id'] % 97) + 1)
result = weighted.groupby(selected['category'], sort=True).sum()
print('TOTAL:' + json.dumps({str(k): int(v) for k, v in result.items()}, sort_keys=True, separators=(',', ':')))
""",
    "etl_streaming": """import csv
import json
totals = {}
with open('transactions.csv', newline='') as handle:
    reader = csv.reader(handle)
    header = next(reader)
    account_i, category_i, amount_i = (header.index(name) for name in ('account_id', 'category', 'amount_cents'))
    for row in reader:
        account = int(row[account_i])
        if account % 11 < 7:
            key = row[category_i]
            totals[key] = totals.get(key, 0) + int(row[amount_i]) * ((account % 97) + 1)
print('TOTAL:' + json.dumps(totals, sort_keys=True, separators=(',', ':')))
""",
}


def make_contract(memory_mib: int = 1024, wall_seconds: float = 90):
    evidence = RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1", target_id="gcp-e0b-calibration",
        observed_at_utc=datetime.now(timezone.utc).isoformat(), source="model-free-reference",
        memory_max_bytes=memory_mib * 1024 * 1024, cpu_quota_cores=1,
        wall_time_limit_seconds=wall_seconds, runtime="CPython 3.11.2",
        packages=("numpy==2.0.2", "pandas==2.2.3"),
    )
    return ContractCompiler().compile(evidence)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"), required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()
    common = dict(host=args.host, user="manuagrawal",
                  identity_file=Path.home() / ".ssh" / "google_compute_engine",
                  worker_local_path=ROOT / "benchmarks" / "aether_execution_worker.py")
    no_assets = SSHLinuxExecutionBackend(**common)
    numerical = SSHLinuxExecutionBackend(**common, assets={"vectors.npy": "/opt/aether-data/vectors.npy"})
    etl = SSHLinuxExecutionBackend(**common, assets={"transactions.csv": "/opt/aether-data/transactions.csv"})
    records = []
    for name, program in PROGRAMS.items():
        backend = numerical if name.startswith("numerical_") else etl if name.startswith("etl_") else no_assets
        for repetition in range(1, args.repetitions + 1):
            observation = backend.run(program, make_contract())
            records.append({"name": name, "repetition": repetition, "observation": observation.to_dict()})
            if observation.exit_code != 0:
                raise RuntimeError(f"{name} repetition {repetition} failed: {observation}")
    numerical_outputs = sorted({
        r["observation"]["stdout"].strip()
        for r in records if r["name"].startswith("numerical_")
    })
    numerical_values = [float(value.removeprefix("TOTAL:")) for value in numerical_outputs]
    numerical_relative_span = (max(numerical_values) - min(numerical_values)) / max(abs(v) for v in numerical_values)
    numerical_rtol = 1e-8
    if numerical_relative_span > numerical_rtol:
        raise RuntimeError(f"numerical references exceed rtol={numerical_rtol}: {numerical_outputs}")
    etl_outputs = {
        r["observation"]["stdout"].strip()
        for r in records if r["name"].startswith("etl_")
    }
    if len(etl_outputs) != 1:
        raise RuntimeError(f"ETL reference outputs disagree: {etl_outputs}")
    outputs = {
        "numerical": numerical_outputs,
        "numerical_relative_span": numerical_relative_span,
        "numerical_rtol": numerical_rtol,
        "etl": etl_outputs.pop(),
    }
    summary = {}
    for name in PROGRAMS:
        subset = [r["observation"] for r in records if r["name"] == name]
        summary[name] = {
            "n": len(subset),
            "memory_peak_bytes": [r["memory_peak_bytes"] for r in subset],
            "memory_peak_median_bytes": int(statistics.median(r["memory_peak_bytes"] for r in subset)),
            "program_time_seconds": [r["program_time_seconds"] for r in subset],
            "program_time_median_seconds": statistics.median(r["program_time_seconds"] for r in subset),
        }
    payload = {
        "schema_version": "e0b-reference-calibration/v0.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repetitions": args.repetitions,
        "dataset_manifest": {
            "vectors.npy": {"bytes": 32768128, "sha256": "b95a6f21f8c055e4dff0ea6b51cec50f7f460809d5e93f8a0a2bb9f9717b9ba9"},
            "transactions.csv": {"bytes": 38333733, "sha256": "26c0b06bb123664d48b08243b30b48a5c1a5bd1e4df68bed75d9f06e0069313b"}
        },
        "reference_outputs": outputs,
        "summary": summary,
        "records": records,
    }
    output = ROOT / "experiments" / "09_aamas_contract_bridge" / "calibration" / "e0b_reference_calibration.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
