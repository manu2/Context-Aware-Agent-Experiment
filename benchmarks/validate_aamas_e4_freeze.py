#!/usr/bin/env python3
"""Fail-closed validation of the AAMAS confirmatory protocol freeze."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "experiments/09_aamas_contract_bridge/protocol"
TASKS = PROTOCOL / "tasks"
MANIFESTS = [
    PROTOCOL / "confirmatory_gemini38.json",
    PROTOCOL / "confirmatory_openai_sol.json",
    PROTOCOL / "confirmatory_anthropic_sonnet.json",
]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    runner_path = ROOT / "benchmarks/run_aamas_e2_canary.py"
    spec = importlib.util.spec_from_file_location("aamas_runner", runner_path)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    checks = {}
    calibration = json.loads((ROOT / "experiments/09_aamas_contract_bridge/calibration/e4_secondary_instance_calibration.json").read_text())
    failed_calibration = json.loads((ROOT / "experiments/09_aamas_contract_bridge/calibration/e4_secondary_instance_calibration_attempt1_failed.json").read_text())
    checks["secondary_calibration_passes"] = calibration["passed"] and all(calibration["checks"].values())
    checks["failed_calibration_preserved"] = not failed_calibration["passed"]
    expected_assets = {
        "vectors_secondary.npy": (32768128, "75525cd7fdaba7b2f4d87dbbfcada9b66c4f4092ed4a91520690ead608917410"),
        "transactions_secondary.csv": (39444783, "8bd326864973b149f76995d6714bc50546b19208ea5fa9ff5e34750a6c8f7aba"),
    }
    for filename in ("numerical_primary.json", "numerical_secondary.json", "etl_primary.json", "etl_secondary.json"):
        task = json.loads((TASKS / filename).read_text())
        checks[f"task_schema_{filename}"] = task["schema_version"] == "aamas-task/v0.1"
        if task["asset"]["name"] in expected_assets:
            size, asset_hash = expected_assets[task["asset"]["name"]]
            checks[f"asset_{filename}"] = task["asset"]["bytes"] == size and task["asset"]["sha256"] == asset_hash
    total_budget = 0.0
    hashes = {}
    campaign_order = []
    for path in MANIFESTS:
        manifest = json.loads(path.read_text())
        campaign_order.append((manifest["campaign_priority"], manifest["model"]["id"]))
        order = runner.execution_order(manifest)
        counts = Counter(tuple(row) for row in order)
        checks[f"order_{path.stem}"] = len(order) == 96 and len(counts) == 24 and set(counts.values()) == {4}
        checks[f"calls_{path.stem}"] = manifest["maximum_provider_calls"] == 192
        checks[f"pristine_{path.stem}"] = not any((ROOT / "experiments/09_aamas_contract_bridge/confirmatory").glob(manifest["run_id_prefix"] + "-*"))
        total_budget += manifest["budget_usd"]
        hashes[str(path.relative_to(ROOT))] = digest(path)
    checks["aggregate_budget_usd_30"] = abs(total_budget - 30.0) < 1e-9
    checks["cheapest_provider_runs_first"] = sorted(campaign_order)[0] == (1, "gemini-3.8-flash")
    checks["campaign_priorities_unique"] = sorted(priority for priority, _ in campaign_order) == [1, 2, 3]
    pilot = json.loads((ROOT / "experiments/09_aamas_contract_bridge/api_pilot/pilot_analysis.json").read_text())
    checks["strategy_codebook_no_pilot_first_pass_ambiguity"] = all(
        cell["adjudication_required"] == 0 for cell in pilot["cell_summary"].values()
    )
    required = [
        PROTOCOL / "CONFIRMATORY_ANALYSIS_PLAN.md",
        ROOT / "docs/20_aamas_strategy_codebook.md",
        ROOT / "src/aether_contract_bridge/strategy.py",
        ROOT / "src/aether_contract_bridge/provider.py",
        ROOT / "src/aether_contract_bridge/pipeline.py",
        ROOT / "src/aether_contract_bridge/execution.py",
        ROOT / "src/aether_contract_bridge/scoring.py",
        ROOT / "src/aether_contract_bridge/compiler.py",
        ROOT / "src/aether_contract_bridge/rendering.py",
        ROOT / "src/aether_contract_bridge/recording.py",
        ROOT / "benchmarks/aether_execution_worker.py",
        ROOT / "benchmarks/run_aamas_e2_canary.py",
    ]
    checks["analysis_and_codebook_present"] = all(path.exists() for path in required)
    hashes.update({str(path.relative_to(ROOT)): digest(path) for path in required})
    payload = {
        "schema_version": "aamas-e4-freeze-validation/v1.0",
        "passed": all(checks.values()), "checks": checks,
        "aggregate_budget_usd": total_budget, "protocol_sha256": hashes,
    }
    output = ROOT / "experiments/09_aamas_contract_bridge/protocol/E4_FREEZE_VALIDATION.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
