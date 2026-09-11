#!/usr/bin/env python3
"""Run the E0a development-only fixture through the production-shaped path."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aether_contract_bridge.execution import SSHLinuxExecutionBackend
from aether_contract_bridge.generation import ImportedResponseBackend
from aether_contract_bridge.models import RawSubstrateEvidence
from aether_contract_bridge.pipeline import run_trajectory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"), required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--user", default=os.environ.get("AETHER_WORKER_USER", "manuagrawal"))
    parser.add_argument("--identity-file", type=Path,
                        default=Path.home() / ".ssh" / "google_compute_engine")
    parser.add_argument("--deploy-worker", action="store_true")
    args = parser.parse_args()

    backend = SSHLinuxExecutionBackend(
        host=args.host, user=args.user, identity_file=args.identity_file,
        worker_local_path=ROOT / "benchmarks" / "aether_execution_worker.py",
    )
    if args.deploy_worker:
        backend.deploy()
    evidence = RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1",
        target_id="gcp://project-a9fc9225-58b8-41d1-bac/us-central1-a/aether-aamas-worker",
        observed_at_utc=datetime.now(timezone.utc).isoformat(),
        source="frozen-e0a-fixture",
        memory_max_bytes=64 * 1024 * 1024,
        cpu_quota_cores=1.0,
        wall_time_limit_seconds=5.0,
        runtime="CPython 3.11 / Debian 12",
    )
    fixture = (ROOT / "experiments" / "09_aamas_contract_bridge" / "fixtures" / "response_sum.py.txt").read_text()
    trajectory_id = "e0a-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary = run_trajectory(
        trajectory_id=trajectory_id,
        task="Write a Python program that sums the integers from 1 through 100 and prints TOTAL:<value>.",
        condition="P", evidence=evidence,
        generation_backend=ImportedResponseBackend(fixture, "e0a-sum-fixture"),
        execution_backend=backend,
        archive_root=ROOT / "experiments" / "09_aamas_contract_bridge" / "development_smoke",
        correctness_oracle=lambda output: output.strip() == "TOTAL:5050",
    )
    payload = json.loads(summary.read_text())
    print(json.dumps({"summary": str(summary), "score": payload["score"],
                      "execution": payload["execution"]}, indent=2))
    return 0 if payload["score"]["suitable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
