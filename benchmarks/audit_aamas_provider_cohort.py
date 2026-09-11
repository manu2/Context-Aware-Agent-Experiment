#!/usr/bin/env python3
"""Fail-closed integrity and outcome audit for one confirmatory provider cohort."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from math import sqrt
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aether_contract_bridge.models import ExecutionContract
from aether_contract_bridge.rendering import ContractRenderer

BASE = ROOT / "experiments/09_aamas_contract_bridge"
PROTOCOL = BASE / "protocol"
ARCHIVE = BASE / "confirmatory"


def order(manifest: dict) -> list[list[str]]:
    if "execution_order" in manifest:
        return manifest["execution_order"]
    import random
    matrix = manifest["matrix"]
    rows = [[family, instance, environment, condition]
            for family, instances in matrix["instances"].items()
            for instance in instances for environment in matrix["environments"]
            for condition in matrix["conditions"]
            for _ in range(matrix["repetitions_per_cell"])]
    random.Random(manifest["order_seed"]).shuffle(rows)
    return rows


def wilson(successes: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [center - margin, center + margin]


def trajectory_id(prefix: str, index: int, entry: list[str]) -> str:
    family, instance, environment, condition = entry
    return f"{prefix}-{index:03d}-{family}-{instance}-{environment}-{condition}"


def audit_complete(directory: Path, expected_entry: list[str], model_id: str) -> list[str]:
    issues = []
    summary = json.loads((directory / "summary.json").read_text())
    snapshot = json.loads((directory / "trajectory_manifest.json").read_text())
    family, _, environment, condition = expected_entry
    spec = snapshot["task_spec"]
    envelope = spec["environments"][environment]
    contract = ExecutionContract(
        schema_version="execution-contract/v0.1", target_id=f"gcp-canary-{family}-{environment}",
        memory_max_bytes=envelope["memory_mib"] * 1024 * 1024,
        cpu_quota_cores=envelope["cpu_cores"], wall_time_limit_seconds=envelope["wall_seconds"],
        runtime="CPython 3.11.2", packages=("numpy==2.0.2", "pandas==2.2.3"),
        evidence_hash="sha256:" + "0" * 64,
    )
    if snapshot["execution_entry"] != expected_entry:
        issues.append("execution entry mismatch")
    if (directory / "prompt.txt").read_text() != ContractRenderer().render(spec["prompt"], condition, contract):
        issues.append("initial prompt mismatch")
    if summary.get("status") != "complete" or summary.get("condition") != condition:
        issues.append("summary status/condition mismatch")
    attempts = summary.get("attempts", [])
    if summary.get("attempt_count") != len(attempts) or len(attempts) not in (1, 2):
        issues.append("invalid attempt count")
    if len(attempts) == 2 and attempts[0]["score"]["suitable"]:
        issues.append("unnecessary second attempt")
    if attempts:
        if summary.get("first_pass_suitable") != attempts[0]["score"]["suitable"]:
            issues.append("first-pass score mismatch")
        if summary.get("final_suitable") != attempts[-1]["score"]["suitable"]:
            issues.append("final score mismatch")
    for attempt in attempts:
        number = attempt["attempt"]
        for name in (f"attempt_{number}_program.py", f"attempt_{number}_raw_response.txt",
                     f"attempt_{number}_provider_response.json", f"attempt_{number}_strategy.json"):
            if not (directory / name).exists():
                issues.append(f"missing {name}")
        if attempt["generation"]["model"] != model_id:
            issues.append(f"model mismatch on attempt {number}")
        execution, score = attempt["execution"], attempt["score"]
        if score["within_time"] != (execution["program_time_seconds"] <= envelope["wall_seconds"]):
            issues.append(f"time score mismatch on attempt {number}")
        measured_within = execution["memory_peak_bytes"] is not None and execution["memory_peak_bytes"] <= contract.memory_max_bytes
        if score["within_memory"] != measured_within:
            issues.append(f"memory score mismatch on attempt {number}")
        expected_suitable = score["correct"] and score["within_memory"] and score["within_time"] and not execution["oom_killed"] and not execution["timed_out"]
        if score["suitable"] != expected_suitable:
            issues.append(f"suitability mismatch on attempt {number}")
    return issues


def failure_type(attempt: dict) -> str | None:
    execution, score = attempt["execution"], attempt["score"]
    if score["suitable"]:
        return None
    if execution.get("oom_killed"):
        return "oom_kill"
    if execution.get("timed_out"):
        return "timeout"
    if not score.get("correct"):
        return "incorrect_or_runtime_error"
    if not score.get("within_memory"):
        return "memory_exceedance"
    if not score.get("within_time"):
        return "time_exceedance"
    return "other"


def compact_attempt(attempt: dict) -> dict:
    execution, score = attempt["execution"], attempt["score"]
    metadata = attempt["generation"].get("request_metadata", {})
    return {
        "attempt": attempt["attempt"],
        "correct": bool(score["correct"]),
        "suitable": bool(score["suitable"]),
        "within_memory": bool(score["within_memory"]),
        "within_time": bool(score["within_time"]),
        "failure_type": failure_type(attempt),
        "program_time_seconds": execution.get("program_time_seconds"),
        "worker_time_seconds": execution.get("worker_time_seconds"),
        "memory_peak_bytes": execution.get("memory_peak_bytes"),
        "memory_exceedance_bytes": score.get("memory_exceedance_bytes"),
        "oom_killed": bool(execution.get("oom_killed")),
        "timed_out": bool(execution.get("timed_out")),
        "input_tokens": metadata.get("input_tokens"),
        "output_tokens_including_thoughts": metadata.get("output_tokens_including_thoughts"),
        "generation_seconds": metadata.get("generation_seconds"),
        "estimated_cost_usd": metadata.get("estimated_cost_usd"),
        "strategy": attempt["strategy"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest_path = PROTOCOL / Path(args.manifest).name
    manifest = json.loads(manifest_path.read_text())
    prefix, model_id = manifest["run_id_prefix"], manifest["model"]["id"]

    replacements = {}
    for path in ARCHIVE.glob("*/trajectory_manifest.json"):
        snapshot = json.loads(path.read_text())
        replaced = snapshot.get("infrastructure_replacement_for")
        if replaced:
            replacements[replaced] = path.parent

    rows, issues, incomplete, infrastructure = [], [], [], []
    for index, entry in enumerate(order(manifest), 1):
        original_id = trajectory_id(prefix, index, entry)
        original = ARCHIVE / original_id
        summary = json.loads((original / "summary.json").read_text()) if (original / "summary.json").exists() else None
        selected = original if summary and summary.get("status") == "complete" else replacements.get(original_id)
        if selected is None or not (selected / "summary.json").exists():
            incomplete.append(original_id)
            if summary and summary.get("status") == "failed":
                infrastructure.append({"trajectory_id": original_id, "error_type": summary.get("error_type"), "error": summary.get("error")})
            continue
        selected_summary = json.loads((selected / "summary.json").read_text())
        local_issues = audit_complete(selected, entry, model_id)
        issues.extend({"trajectory_id": selected.name, "issue": issue} for issue in local_issues)
        compact_attempts = [compact_attempt(attempt) for attempt in selected_summary["attempts"]]
        rows.append({
            "scheduled_trajectory_id": original_id, "effective_trajectory_id": selected.name,
            "family": entry[0], "instance": entry[1], "environment": entry[2], "condition": entry[3],
            "first_pass_suitable": bool(selected_summary["first_pass_suitable"]),
            "final_suitable": bool(selected_summary["final_suitable"]),
            "attempt_count": selected_summary["attempt_count"],
            "attempts": compact_attempts,
            "provider_tokens": sum(
                (attempt["input_tokens"] or 0) + (attempt["output_tokens_including_thoughts"] or 0)
                for attempt in compact_attempts
            ),
            "estimated_cost_usd": sum(attempt["estimated_cost_usd"] or 0 for attempt in compact_attempts),
            "end_to_end_seconds": sum(
                (attempt["generation_seconds"] or 0) + (attempt["worker_time_seconds"] or 0)
                for attempt in compact_attempts
            ),
        })

    conditions = {}
    for condition in "PRG":
        subset = [row for row in rows if row["condition"] == condition]
        first = sum(row["first_pass_suitable"] for row in subset)
        final = sum(row["final_suitable"] for row in subset)
        conditions[condition] = {
            "n": len(subset), "first_pass_suitable": first,
            "first_pass_wilson_95": wilson(first, len(subset)),
            "final_suitable": final, "final_wilson_95": wilson(final, len(subset)),
            "provider_calls": sum(row["attempt_count"] for row in subset),
        }
    payload = {
        "schema_version": "aamas-provider-cohort-audit/v1.1", "manifest": str(manifest_path.relative_to(ROOT)),
        "model": model_id, "scheduled": len(order(manifest)), "complete": len(rows),
        "incomplete": incomplete, "infrastructure_failures": infrastructure,
        "integrity_issues": issues, "condition_summary": conditions, "rows": rows,
        "passed": not issues and not incomplete,
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: payload[key] for key in ("scheduled", "complete", "passed", "condition_summary")}, indent=2))
    if issues or (incomplete and not args.allow_incomplete):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
