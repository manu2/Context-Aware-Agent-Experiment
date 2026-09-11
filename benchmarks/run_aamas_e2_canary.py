#!/usr/bin/env python3
"""Run or safely resume the frozen 12-trajectory direct-API canary."""

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
from aether_contract_bridge.models import RawSubstrateEvidence
from aether_contract_bridge.pipeline import run_trajectory
from aether_contract_bridge.provider import (
    AnthropicMessagesBackend,
    BudgetLedger,
    GeminiDirectAPIBackend,
    OpenAIResponsesBackend,
    load_dotenv,
)


EXPECTED_ETL = {"A": 584859984000, "B": 582445702800, "C": 584178107400, "D": 585658510500,
                "E": 584768685600, "F": 583789773900, "G": 584327166000, "H": 585146828400}


def numerical_oracle(output: str) -> bool:
    try:
        return math.isclose(float(output.strip().removeprefix("TOTAL:")), 835795650.00869,
                            rel_tol=1e-6, abs_tol=1e-3)
    except ValueError:
        return False


def etl_oracle(output: str) -> bool:
    try:
        prefix, value = output.strip().split(":", 1)
        return prefix == "TOTAL" and json.loads(value) == EXPECTED_ETL
    except (ValueError, json.JSONDecodeError):
        return False


def generation_backend(manifest: dict, ledger: BudgetLedger):
    model = manifest["model"]
    common = {"ledger": ledger, "model": model["id"],
              "development_only": manifest.get("development_only", False)}
    if model["provider"] == "google":
        return GeminiDirectAPIBackend(
            api_key=os.environ.get("GEMINI_API_KEY", ""), **common,
            temperature=model.get("temperature"), top_p=model.get("top_p"),
            thinking_level=model.get("thinking_level"),
            max_output_tokens=model["max_output_tokens"],
        )
    if model["provider"] == "openai":
        prices = model["pricing_usd_per_million_tokens"]
        return OpenAIResponsesBackend(
            api_key=os.environ.get("OPENAI_API_KEY", ""), **common,
            reasoning_effort=model["reasoning_effort"],
            max_output_tokens=model["max_output_tokens"],
            input_usd_per_million=prices["input"],
            cached_input_usd_per_million=prices.get("cached_input", prices["input"]),
            output_usd_per_million=prices["output_including_reasoning"],
        )
    if model["provider"] == "anthropic":
        prices = model["pricing_usd_per_million_tokens"]
        return AnthropicMessagesBackend(
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""), **common,
            effort=model["effort"], max_tokens=model["max_output_tokens"],
            input_usd_per_million=prices["input"],
            output_usd_per_million=prices["output_including_thinking"],
        )
    raise ValueError(f"unsupported provider: {model['provider']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"), required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--manifest", default="canary_manifest.json")
    args = parser.parse_args()
    if Path(args.manifest).name != args.manifest or not args.manifest.endswith(".json"):
        parser.error("--manifest must be a JSON filename without directories")
    load_dotenv(ROOT / ".env")
    manifest = json.loads((ROOT / "experiments/09_aamas_contract_bridge/protocol" / args.manifest).read_text())
    task_specs = {name: json.loads((ROOT / f"experiments/09_aamas_contract_bridge/protocol/tasks/{name}_primary.json").read_text())
                  for name in ("numerical", "etl")}
    archive_subdir = manifest.get("archive_subdir", "api_canary")
    if Path(archive_subdir).name != archive_subdir:
        parser.error("archive_subdir in the manifest must be one directory name")
    canary_root = ROOT / "experiments/09_aamas_contract_bridge" / archive_subdir
    canary_root.mkdir(parents=True, exist_ok=True)
    budget_usd = manifest.get("budget_usd", manifest.get("canary_budget_usd"))
    if budget_usd is None:
        parser.error("manifest must declare budget_usd")
    ledger = BudgetLedger(canary_root / manifest["budget_ledger_file"], hard_cap_usd=budget_usd,
                          max_calls=manifest["maximum_provider_calls"])
    generation = generation_backend(manifest, ledger)
    prefix = manifest["run_id_prefix"]
    attempted = []
    for index, (family, environment, condition) in enumerate(manifest["execution_order"], 1):
        trajectory_id = f"{prefix}-{index:02d}-{family}-{environment}-{condition}"
        directory = canary_root / trajectory_id
        if directory.exists():
            attempted.append({"trajectory_id": trajectory_id, "status": "already_archived"})
            continue
        spec = task_specs[family]
        envelope = spec["environments"][environment]
        evidence = RawSubstrateEvidence(
            schema_version="raw-substrate-evidence/v0.1",
            target_id=f"gcp-canary-{family}-{environment}",
            observed_at_utc=datetime.now(timezone.utc).isoformat(), source="frozen-canary-contract",
            memory_max_bytes=envelope["memory_mib"] * 1024 * 1024,
            cpu_quota_cores=envelope["cpu_cores"], wall_time_limit_seconds=envelope["wall_seconds"],
            runtime="CPython 3.11.2", packages=("numpy==2.0.2", "pandas==2.2.3"),
        )
        asset_name = spec["asset"]["name"]
        execution = SSHLinuxExecutionBackend(
            host=args.host, user="manuagrawal", identity_file=Path.home() / ".ssh/google_compute_engine",
            worker_local_path=ROOT / "benchmarks/aether_execution_worker.py",
            assets={asset_name: f"/opt/aether-data/{asset_name}"},
        )
        if index == 1:
            execution.deploy()
        try:
            summary = run_trajectory(
                trajectory_id=trajectory_id, task=spec["prompt"], condition=condition,
                evidence=evidence, generation_backend=generation, execution_backend=execution,
                archive_root=canary_root,
                correctness_oracle=numerical_oracle if family == "numerical" else etl_oracle,
            )
            attempted.append({"trajectory_id": trajectory_id, "status": "complete", "summary": str(summary.relative_to(ROOT))})
        except Exception as exc:
            attempted.append({"trajectory_id": trajectory_id, "status": "failed", "error_type": type(exc).__name__,
                              "error": str(exc)})
    summaries = []
    for directory in sorted(canary_root.glob(prefix + "-*")):
        path = directory / "summary.json"
        if path.exists():
            summaries.append(json.loads(path.read_text()))
    report = {
        "schema_version": manifest.get("report_schema", "aamas-canary-report/v0.1"),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "development_only": manifest.get("development_only", False), "attempted_this_invocation": attempted,
        "trajectory_count": len(summaries), "complete_count": sum(s.get("status") == "complete" for s in summaries),
        "first_pass_suitable": sum(bool(s.get("first_pass_suitable")) for s in summaries),
        "final_suitable": sum(bool(s.get("final_suitable")) for s in summaries),
        "summaries": summaries,
    }
    (canary_root / f"{prefix}_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in ("trajectory_count", "complete_count", "first_pass_suitable", "final_suitable")}, indent=2))
    return 0 if report["trajectory_count"] == len(manifest["execution_order"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
