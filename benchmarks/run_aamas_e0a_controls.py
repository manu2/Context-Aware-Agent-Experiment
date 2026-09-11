#!/usr/bin/env python3
"""Archive fail-closed cgroup v2 memory and timeout positive controls."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aether_contract_bridge.compiler import ContractCompiler
from aether_contract_bridge.execution import SSHLinuxExecutionBackend
from aether_contract_bridge.models import RawSubstrateEvidence


def contract(memory_mib: int, wall_seconds: float):
    evidence = RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1", target_id="gcp-e0a-positive-control",
        observed_at_utc=datetime.now(timezone.utc).isoformat(), source="predeclared-positive-control",
        memory_max_bytes=memory_mib * 1024 * 1024, cpu_quota_cores=1,
        wall_time_limit_seconds=wall_seconds, runtime="CPython 3.11 / Debian 12",
    )
    return ContractCompiler().compile(evidence)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"), required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--user", default=os.environ.get("AETHER_WORKER_USER", "manuagrawal"))
    parser.add_argument("--identity-file", type=Path,
                        default=Path.home() / ".ssh" / "google_compute_engine")
    parser.add_argument("--output-name", default="e0a_positive_controls.json")
    args = parser.parse_args()
    backend = SSHLinuxExecutionBackend(
        host=args.host, user=args.user, identity_file=args.identity_file,
        worker_local_path=ROOT / "benchmarks" / "aether_execution_worker.py",
    )
    memory = backend.run("x = bytearray(96 * 1024 * 1024)\nprint(len(x))\n", contract(48, 5))
    metering = backend.run("x = bytearray(16 * 1024 * 1024)\nprint(len(x))\n", contract(64, 5))
    timeout = backend.run("import time\ntime.sleep(3)\nprint('UNEXPECTED')\n", contract(64, 1))
    metering_ok = (
        metering.exit_code == 0
        and metering.memory_peak_bytes is not None
        and 16 * 1024 * 1024 <= metering.memory_peak_bytes <= 64 * 1024 * 1024
    )
    passed = memory.oom_killed and not memory.timed_out and metering_ok and timeout.timed_out
    payload = {
        "schema_version": "e0a-positive-controls/v0.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "memory_control_expected": "oom_kill under 48 MiB",
        "memory_control": memory.to_dict(),
        "metering_control_expected": "successful 16 MiB allocation measured between 16 and 64 MiB",
        "metering_control": metering.to_dict(),
        "timeout_control_expected": "timeout under 1 second",
        "timeout_control": timeout.to_dict(),
    }
    if Path(args.output_name).name != args.output_name or not args.output_name.endswith(".json"):
        parser.error("--output-name must be a JSON filename without directories")
    output = ROOT / "experiments" / "09_aamas_contract_bridge" / "calibration" / args.output_name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "passed": passed}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
