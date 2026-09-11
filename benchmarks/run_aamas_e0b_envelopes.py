#!/usr/bin/env python3
"""Validate opposed candidate envelopes before freezing any model-visible contract."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "benchmarks"))

from aether_contract_bridge.compiler import ContractCompiler
from aether_contract_bridge.execution import SSHLinuxExecutionBackend
from aether_contract_bridge.models import RawSubstrateEvidence
from run_aamas_e0b_calibration import PROGRAMS


CELLS = {
    "numerical_memory_tight": {"memory_mib": 128, "wall_seconds": 8, "expected": "numerical_bounded", "opposed": "numerical_eager"},
    "numerical_latency_tight": {"memory_mib": 1024, "wall_seconds": 3.0, "expected": "numerical_eager", "opposed": "numerical_bounded"},
    "etl_memory_tight": {"memory_mib": 128, "wall_seconds": 4, "expected": "etl_streaming", "opposed": "etl_pandas"},
    "etl_latency_tight": {"memory_mib": 512, "wall_seconds": 1.4, "expected": "etl_pandas", "opposed": "etl_streaming"},
}


def make_contract(cell: dict):
    return ContractCompiler().compile(RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1", target_id="gcp-e0b-" + cell["expected"],
        observed_at_utc=datetime.now(timezone.utc).isoformat(), source="calibrated-candidate-envelope",
        memory_max_bytes=cell["memory_mib"] * 1024 * 1024, cpu_quota_cores=1,
        wall_time_limit_seconds=cell["wall_seconds"], runtime="CPython 3.11.2",
        packages=("numpy==2.0.2", "pandas==2.2.3"),
    ))


def successful(observation: dict) -> bool:
    return observation["exit_code"] == 0 and not observation["timed_out"] and not observation["oom_killed"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"), required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--cell", choices=sorted(CELLS))
    parser.add_argument("--label", help="append a filesystem-safe label to the output filename")
    args = parser.parse_args()
    common = dict(host=args.host, user="manuagrawal",
                  identity_file=Path.home() / ".ssh" / "google_compute_engine",
                  worker_local_path=ROOT / "benchmarks" / "aether_execution_worker.py")
    backends = {
        "numerical": SSHLinuxExecutionBackend(**common, assets={"vectors.npy": "/opt/aether-data/vectors.npy"}),
        "etl": SSHLinuxExecutionBackend(**common, assets={"transactions.csv": "/opt/aether-data/transactions.csv"}),
    }
    records = []
    selected = {args.cell: CELLS[args.cell]} if args.cell else CELLS
    for cell_name, cell in selected.items():
        family = cell_name.split("_", 1)[0]
        contract = make_contract(cell)
        for role in ("expected", "opposed"):
            program_name = cell[role]
            for repetition in range(1, args.repetitions + 1):
                observation = backends[family].run(PROGRAMS[program_name], contract)
                records.append({"cell": cell_name, "role": role, "program": program_name,
                                "repetition": repetition, "contract": contract.to_dict(),
                                "observation": observation.to_dict()})
    checks = {}
    passed = True
    for cell_name in selected:
        expected = [r for r in records if r["cell"] == cell_name and r["role"] == "expected"]
        opposed = [r for r in records if r["cell"] == cell_name and r["role"] == "opposed"]
        expected_passes = sum(successful(r["observation"]) for r in expected)
        opposed_passes = sum(successful(r["observation"]) for r in opposed)
        cell_passed = expected_passes == args.repetitions and opposed_passes == 0
        passed = passed and cell_passed
        checks[cell_name] = {"expected_passes": expected_passes, "opposed_passes": opposed_passes,
                             "n_each": args.repetitions, "passed": cell_passed}
    payload = {"schema_version": "e0b-opposed-envelopes/v0.1",
               "created_at_utc": datetime.now(timezone.utc).isoformat(),
               "passed": passed, "cells": CELLS, "checks": checks, "records": records}
    if args.label and not re.fullmatch(r"[A-Za-z0-9_-]+", args.label):
        parser.error("--label may contain only letters, digits, underscores, and hyphens")
    suffix = f"_{args.cell}_margin" if args.cell else ""
    if args.label:
        suffix += f"_{args.label}"
    output = ROOT / "experiments" / "09_aamas_contract_bridge" / "calibration" / f"e0b_opposed_envelopes{suffix}.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "passed": passed, "checks": checks}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
