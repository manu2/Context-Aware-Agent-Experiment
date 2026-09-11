#!/usr/bin/env python3
"""Verify that generated programs execute unprivileged, offline, and read-only."""

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


def contract():
    return ContractCompiler().compile(RawSubstrateEvidence(
        schema_version="raw-substrate-evidence/v0.1",
        target_id="gcp-pre-pilot-sandbox-control",
        observed_at_utc=datetime.now(timezone.utc).isoformat(),
        source="predeclared-sandbox-control",
        memory_max_bytes=64 * 1024 * 1024,
        cpu_quota_cores=1,
        wall_time_limit_seconds=5,
        runtime="CPython 3.11.2 / Debian 12",
    ))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"),
                        required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--output-name", default="e0_pre_pilot_security_controls.json")
    args = parser.parse_args()
    if Path(args.output_name).name != args.output_name or not args.output_name.endswith(".json"):
        parser.error("--output-name must be a JSON filename without directories")

    common = dict(host=args.host, user="manuagrawal",
                  identity_file=Path.home() / ".ssh" / "google_compute_engine",
                  worker_local_path=ROOT / "benchmarks" / "aether_execution_worker.py")
    plain = SSHLinuxExecutionBackend(**common)
    with_asset = SSHLinuxExecutionBackend(**common, assets={"vectors.npy": "/opt/aether-data/vectors.npy"})

    identity = plain.run("import os\nprint(f'UID={os.geteuid()}')\n", contract())
    filesystem = with_asset.run(
        "import os\nprint(f'WRITABLE={os.access(\"vectors.npy\", os.W_OK)}')\n",
        contract(),
    )
    network = plain.run(
        "import socket\n"
        "s=socket.socket(); s.settimeout(1)\n"
        "try:\n"
        "    s.connect(('1.1.1.1', 80)); print('NETWORK_OPEN')\n"
        "except OSError as exc:\n"
        "    print(f'NETWORK_BLOCKED={exc.errno}')\n",
        contract(),
    )
    checks = {
        "non_root_uid": identity.exit_code == 0 and identity.stdout.strip().startswith("UID=")
                        and identity.stdout.strip() != "UID=0",
        "dataset_read_only": filesystem.exit_code == 0 and filesystem.stdout.strip() == "WRITABLE=False",
        "network_isolated": network.exit_code == 0 and network.stdout.strip().startswith("NETWORK_BLOCKED="),
    }
    passed = all(checks.values())
    payload = {
        "schema_version": "aamas-sandbox-controls/v0.1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "checks": checks,
        "identity": identity.to_dict(),
        "filesystem": filesystem.to_dict(),
        "network": network.to_dict(),
    }
    output = ROOT / "experiments" / "09_aamas_contract_bridge" / "calibration" / args.output_name
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "passed": passed, "checks": checks}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
