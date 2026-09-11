#!/usr/bin/env python3
"""Run or safely resume the frozen 12-trajectory direct-API canary."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import random
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
    ProviderRequestError,
    load_dotenv,
)
from aether_contract_bridge.strategy import classify_strategy


def oracle_for(family: str, spec: dict):
    if family == "numerical":
        expected = spec["oracle"]["expected_approximately"]
        relative = spec["oracle"]["relative_tolerance"]
        absolute = spec["oracle"]["absolute_tolerance"]

        def numerical(output: str) -> bool:
            try:
                return math.isclose(float(output.strip().removeprefix("TOTAL:")), expected,
                                    rel_tol=relative, abs_tol=absolute)
            except ValueError:
                return False
        return numerical
    expected = spec["oracle"]["expected"]

    def etl(output: str) -> bool:
        try:
            prefix, value = output.strip().split(":", 1)
            return prefix == "TOTAL" and json.loads(value) == expected
        except (ValueError, json.JSONDecodeError):
            return False
    return etl


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


def execution_order(manifest: dict) -> list[list[str]]:
    if "execution_order" in manifest:
        return manifest["execution_order"]
    matrix = manifest["matrix"]
    order = [
        [family, instance, environment, condition]
        for family, instances in matrix["instances"].items()
        for instance in instances
        for environment in matrix["environments"]
        for condition in matrix["conditions"]
        for _ in range(matrix["repetitions_per_cell"])
    ]
    random.Random(manifest["order_seed"]).shuffle(order)
    return order


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("AETHER_WORKER_HOST"), required=os.environ.get("AETHER_WORKER_HOST") is None)
    parser.add_argument("--manifest", default="canary_manifest.json")
    args = parser.parse_args()
    if Path(args.manifest).name != args.manifest or not args.manifest.endswith(".json"):
        parser.error("--manifest must be a JSON filename without directories")
    load_dotenv(ROOT / ".env")
    manifest = json.loads((ROOT / "experiments/09_aamas_contract_bridge/protocol" / args.manifest).read_text())
    task_files = manifest.get("task_files", {
        "numerical_primary": "numerical_primary.json", "etl_primary": "etl_primary.json",
    })
    task_specs = {key: json.loads((ROOT / "experiments/09_aamas_contract_bridge/protocol/tasks" / filename).read_text())
                  for key, filename in task_files.items()}
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
    order = execution_order(manifest)
    attempted = []
    deployed = False
    for index, entry in enumerate(order, 1):
        if len(entry) == 3:
            family, environment, condition = entry
            instance = "primary"
            trajectory_id = f"{prefix}-{index:02d}-{family}-{environment}-{condition}"
        elif len(entry) == 4:
            family, instance, environment, condition = entry
            trajectory_id = f"{prefix}-{index:03d}-{family}-{instance}-{environment}-{condition}"
        else:
            raise ValueError(f"invalid execution-order entry: {entry}")
        task_key = f"{family}_{instance}"
        directory = canary_root / trajectory_id
        if directory.exists():
            attempted.append({"trajectory_id": trajectory_id, "status": "already_archived"})
            continue
        spec = task_specs[task_key]
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
        if not deployed:
            execution.deploy()
            deployed = True
        try:
            protocol_snapshot = {"study_manifest": manifest, "task_spec": spec,
                                 "execution_index": index, "execution_entry": entry}
            resume = manifest.get("infrastructure_resume")
            if resume is not None:
                protocol_snapshot["infrastructure_replacement_for"] = resume["replacement_for"][index - 1]
            summary = run_trajectory(
                trajectory_id=trajectory_id, task=spec["prompt"], condition=condition,
                evidence=evidence, generation_backend=generation, execution_backend=execution,
                archive_root=canary_root,
                correctness_oracle=oracle_for(family, spec),
                protocol_snapshot=protocol_snapshot,
                strategy_classifier=lambda source: classify_strategy(family, source).to_dict(),
            )
            attempted.append({"trajectory_id": trajectory_id, "status": "complete", "summary": str(summary.relative_to(ROOT))})
        except ProviderRequestError as exc:
            attempted.append({"trajectory_id": trajectory_id, "status": "failed", "error_type": type(exc).__name__,
                              "error": str(exc), "provider_status_code": exc.status_code,
                              "campaign_stopped": True})
            break
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
    return 0 if report["complete_count"] == len(order) else 1


if __name__ == "__main__":
    raise SystemExit(main())
