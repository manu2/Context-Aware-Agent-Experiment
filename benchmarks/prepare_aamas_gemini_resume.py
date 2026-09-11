#!/usr/bin/env python3
"""Build and validate the outcome-neutral Gemini E5 resume manifest."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/09_aamas_contract_bridge"
PROTOCOL = BASE / "protocol"
CONFIRMATORY = BASE / "confirmatory"


def main() -> int:
    original = json.loads((PROTOCOL / "confirmatory_gemini38.json").read_text())
    report = json.loads((CONFIRMATORY / "confirm-gemini38-v1_report.json").read_text())
    ledger = json.loads((CONFIRMATORY / "gemini38_budget_ledger.json").read_text())

    failures = []
    for summary in report["summaries"]:
        if summary.get("status") != "failed":
            continue
        if summary.get("attempts"):
            raise RuntimeError(f"generated outcome is not resumable: {summary['trajectory_id']}")
        if summary.get("error_type") not in {"HTTPError", "ProviderRequestError"} or "429" not in summary.get("error", ""):
            raise RuntimeError(f"non-quota failure is not resumable: {summary['trajectory_id']}")
        directory = CONFIRMATORY / summary["trajectory_id"]
        snapshot = json.loads((directory / "trajectory_manifest.json").read_text())
        failures.append((snapshot["execution_index"], summary["trajectory_id"], snapshot["execution_entry"]))

    failures.sort()
    if [index for index, _, _ in failures] != list(range(65, 97)):
        raise RuntimeError("expected only the contiguous 429-affected slots 65..96")

    settled_cost = sum(
        entry.get("estimated_cost_usd", 0.0)
        for entry in ledger["entries"] if entry.get("status") == "complete"
    )
    resume = deepcopy(original)
    resume.update({
        "schema_version": "aamas-confirmatory-infrastructure-resume/v1.0",
        "status": "frozen_before_resume_calls",
        "run_id_prefix": "confirm-gemini38-resume1",
        "budget_ledger_file": "gemini38_resume1_budget_ledger.json",
        "budget_usd": round(original["budget_usd"] - settled_cost, 6),
        "maximum_provider_calls": 64,
        "execution_order": [entry for _, _, entry in failures],
        "infrastructure_resume": {
            "reason": "32 consecutive pre-generation HTTP 429 failures",
            "source_commit": "43c9343",
            "replacement_for": [trajectory_id for _, trajectory_id, _ in failures],
            "original_execution_indices": [index for index, _, _ in failures],
            "selection_rule": "only provider failures with zero generated attempts",
        },
    })
    resume.pop("order_seed", None)
    output = PROTOCOL / "confirmatory_gemini38_resume1.json"
    output.write_text(json.dumps(resume, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)), "slots": len(failures),
        "settled_cost_usd": round(settled_cost, 6),
        "resume_budget_usd": resume["budget_usd"],
        "maximum_provider_calls": resume["maximum_provider_calls"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
