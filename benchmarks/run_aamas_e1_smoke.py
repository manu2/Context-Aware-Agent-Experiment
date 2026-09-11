#!/usr/bin/env python3
"""Execute unedited context-isolated P/R/G development responses."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aether_contract_bridge.execution import SSHLinuxExecutionBackend
from aether_contract_bridge.generation import ImportedResponseBackend
from aether_contract_bridge.models import RawSubstrateEvidence
from aether_contract_bridge.pipeline import run_trajectory


def oracle(output: str) -> bool:
    try:
        value = float(output.strip().removeprefix("TOTAL:"))
    except ValueError:
        return False
    return math.isclose(value, 835795650.00869, rel_tol=1e-6, abs_tol=1e-3)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"), required=os.environ.get("AETHER_WORKER_HOST") is None)
    args = parser.parse_args()
    backend = SSHLinuxExecutionBackend(
        host=args.host, user="manuagrawal",
        identity_file=Path.home() / ".ssh" / "google_compute_engine",
        worker_local_path=ROOT / "benchmarks" / "aether_execution_worker.py",
        assets={"vectors.npy": "/opt/aether-data/vectors.npy"},
    )
    task = json.loads((ROOT / "experiments/09_aamas_contract_bridge/protocol/tasks/numerical_primary.json").read_text())["prompt"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = {}
    for condition in ("P", "R", "G"):
        evidence = RawSubstrateEvidence(
            schema_version="raw-substrate-evidence/v0.1", target_id="gcp-e1-numerical-memory-tight",
            observed_at_utc=datetime.now(timezone.utc).isoformat(), source="frozen-e1-contract",
            memory_max_bytes=128 * 1024 * 1024, cpu_quota_cores=1,
            wall_time_limit_seconds=8, runtime="CPython 3.11.2",
            packages=("numpy==2.0.2", "pandas==2.2.3"),
        )
        fixture_path = ROOT / "experiments/09_aamas_contract_bridge/fixtures" / f"e1_numerical_memory_{condition}.py.txt"
        summary_path = run_trajectory(
            trajectory_id=f"e1-{stamp}-{condition}", task=task, condition=condition,
            evidence=evidence,
            generation_backend=ImportedResponseBackend(fixture_path.read_text(), f"context-isolated-{condition}"),
            execution_backend=backend,
            archive_root=ROOT / "experiments/09_aamas_contract_bridge/development_smoke",
            correctness_oracle=oracle,
        )
        results[condition] = json.loads(summary_path.read_text())
    report = ROOT / "experiments/09_aamas_contract_bridge/development_smoke" / f"e1-{stamp}-report.json"
    report.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: {"score": v["score"], "exit_code": v["execution"]["exit_code"],
                                "peak_mib": None if v["execution"]["memory_peak_bytes"] is None else v["execution"]["memory_peak_bytes"] / 1048576,
                                "program_seconds": v["execution"]["program_time_seconds"]}
                      for k, v in results.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
