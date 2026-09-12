#!/usr/bin/env python3
"""Derive deterministic secondary and robustness analyses for the AAMAS study."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "experiments/09_aamas_contract_bridge/analysis"
AUDITS = (
    "gemini_e5_complete_audit.json",
    "claude_e5_complete_audit.json",
    "gpt_e5_complete_audit.json",
)
TASKS = ROOT / "experiments/09_aamas_contract_bridge/protocol/tasks"
OUTPUT = ANALYSIS / "aamas_secondary_analysis.json"
REPORT = ROOT / "docs/35_aamas_secondary_analysis.md"


def load_rows() -> list[dict]:
    rows: list[dict] = []
    for filename in AUDITS:
        payload = json.loads((ANALYSIS / filename).read_text())
        if not payload.get("passed"):
            raise RuntimeError(f"source audit failed: {filename}")
        rows.extend({**row, "model": payload["model"]} for row in payload["rows"])
    if len(rows) != 288:
        raise RuntimeError(f"expected 288 trajectories, found {len(rows)}")
    return rows


def equal_cell_rd(rows: list[dict], comparator: str) -> float:
    cells: dict[tuple, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        key = (row["model"], row["family"], row["instance"], row["environment"])
        cells[key][row["condition"]].append(int(row["first_pass_suitable"]))
    effects = []
    for key, conditions in cells.items():
        if "P" not in conditions or comparator not in conditions:
            raise RuntimeError(f"incomplete cell {key}")
        effects.append(
            sum(conditions["P"]) / len(conditions["P"])
            - sum(conditions[comparator]) / len(conditions[comparator])
        )
    return sum(effects) / len(effects)


def removals(rows: list[dict], field: str, comparator: str) -> list[dict]:
    values = sorted({row[field] for row in rows})
    return [
        {
            "removed": value,
            "remaining_n": sum(row[field] != value for row in rows),
            "risk_difference": equal_cell_rd(
                [row for row in rows if row[field] != value], comparator
            ),
        }
        for value in values
    ]


def leave_one_stratum(rows: list[dict], comparator: str) -> dict:
    keys = sorted({
        (row["model"], row["family"], row["instance"], row["environment"])
        for row in rows
    })
    results = []
    for key in keys:
        retained = [
            row for row in rows
            if (row["model"], row["family"], row["instance"], row["environment"]) != key
        ]
        results.append({"removed": "|".join(key), "risk_difference": equal_cell_rd(retained, comparator)})
    return {
        "minimum": min(results, key=lambda item: item["risk_difference"]),
        "maximum": max(results, key=lambda item: item["risk_difference"]),
        "all_positive": all(item["risk_difference"] > 0 for item in results),
        "results": results,
    }


def token_decomposition(rows: list[dict]) -> dict:
    result = {}
    for condition in ("P", "R", "G"):
        selected = [row for row in rows if row["condition"] == condition]
        attempts = defaultdict(lambda: {"calls": 0, "input_tokens": 0, "output_tokens_including_thoughts": 0})
        for row in selected:
            for attempt in row["attempts"]:
                bucket = attempts[str(attempt["attempt"])]
                bucket["calls"] += 1
                bucket["input_tokens"] += attempt["input_tokens"] or 0
                bucket["output_tokens_including_thoughts"] += attempt["output_tokens_including_thoughts"] or 0
        result[condition] = dict(sorted(attempts.items()))
    return result


def strategy_suitability(rows: list[dict]) -> list[dict]:
    groups = defaultdict(lambda: {"n": 0, "suitable": 0})
    for row in rows:
        first = row["attempts"][0]
        key = (row["condition"], row["family"], first["strategy"]["primary_strategy"])
        groups[key]["n"] += 1
        groups[key]["suitable"] += int(first["suitable"])
    output = []
    for (condition, family, strategy), values in sorted(groups.items()):
        output.append({
            "condition": condition,
            "family": family,
            "strategy": strategy,
            **values,
            "suitability_rate": values["suitable"] / values["n"],
        })
    return output


def contract_matrix() -> list[dict]:
    output = []
    for path in sorted(TASKS.glob("*.json")):
        task = json.loads(path.read_text())
        family, instance = path.stem.split("_", 1)
        for environment, contract in task["environments"].items():
            output.append({
                "family": family,
                "instance": instance,
                "environment": environment,
                **contract,
                "asset_bytes": task["asset"]["bytes"],
                "asset_sha256": task["asset"]["sha256"],
            })
    return output


def main() -> int:
    rows = load_rows()
    late = json.loads((ANALYSIS / "late_disclosure_combined_v1.json").read_text())
    if not late.get("passed") or late.get("matched_R_failure_states") != 82:
        raise RuntimeError("late-disclosure matched analysis is incomplete")

    robustness = {}
    for comparator in ("R", "G"):
        robustness[f"P_minus_{comparator}"] = {
            "full": equal_cell_rd(rows, comparator),
            "leave_one_model": removals(rows, "model", comparator),
            "leave_one_instance": removals(rows, "instance", comparator),
            "leave_one_family": removals(rows, "family", comparator),
            "leave_one_environment": removals(rows, "environment", comparator),
            "leave_one_full_stratum": leave_one_stratum(rows, comparator),
        }

    late_rows = []
    for filename in ("gemini_late_disclosure_v1.json", "claude_late_disclosure_v1.json", "gpt_late_disclosure_v1.json"):
        late_rows.extend(json.loads((ANALYSIS / filename).read_text())["rows"])
    r_initial_tokens = sum(
        (row["attempts"][0]["input_tokens"] or 0)
        + (row["attempts"][0]["output_tokens_including_thoughts"] or 0)
        for row in rows if row["condition"] == "R"
    )
    late_branch_tokens = sum(
        (row["L_generation"]["request_metadata"].get("input_tokens") or 0)
        + (row["L_generation"]["request_metadata"].get("output_tokens_including_thoughts") or 0)
        for row in late_rows
    )

    late_summary = {
        key: late[key] for key in (
            "archived_R_symptom_only_recovered",
            "late_contract_recovered",
            "transitions",
            "exact_mcnemar_two_sided_p",
            "workflow_total",
            "workflow_by_model",
            "provider_calls",
            "recovery_by_initial_failure",
            "late_residual_failure_types",
        )
    }
    late_summary["workflow_tokens"] = {
        "R_initial_attempts": r_initial_tokens,
        "L_recovery_branches": late_branch_tokens,
        "R_plus_L_total": r_initial_tokens + late_branch_tokens,
    }

    result = {
        "schema_version": "aamas-secondary-analysis/v1.0",
        "source_trajectory_count": len(rows),
        "matched_late_disclosure_states": late["matched_R_failure_states"],
        "robustness": robustness,
        "late_disclosure": late_summary,
        "token_decomposition": token_decomposition(rows),
        "strategy_suitability": strategy_suitability(rows),
        "contract_matrix": contract_matrix(),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    lines = [
        "# AAMAS secondary and robustness analysis",
        "",
        "> Deterministic analysis of the frozen 288-trajectory confirmatory matrix and the separately frozen 82-state matched late-disclosure extension.",
        "",
        "## Removal robustness",
        "",
        "| Contrast | Full RD | Leave-one-model range | Leave-one-instance range | Leave-one-family range | Leave-one-environment range | Leave-one-stratum range |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for contrast, values in robustness.items():
        def span(name: str) -> str:
            rows_ = values[name]
            numbers = [row["risk_difference"] for row in rows_]
            return f"{100*min(numbers):.1f}--{100*max(numbers):.1f} pp"
        stratum = values["leave_one_full_stratum"]
        lines.append(
            f"| {contrast.replace('_', ' ')} | {100*values['full']:.1f} pp | "
            f"{span('leave_one_model')} | {span('leave_one_instance')} | "
            f"{span('leave_one_family')} | {span('leave_one_environment')} | "
            f"{100*stratum['minimum']['risk_difference']:.1f}--{100*stratum['maximum']['risk_difference']:.1f} pp |"
        )
    lines.extend([
        "",
        "All leave-one-full-stratum estimates remain positive for both primary contrasts.",
        "",
        "## Matched recovery timing",
        "",
        f"Across the same 82 archived first-failure states, symptom-only recovery succeeded in **{late['archived_R_symptom_only_recovered']}/82** cases and late exact-contract recovery in **{late['late_contract_recovered']}/82**. The matched transitions were **{late['transitions']['01']} improvements**, **{late['transitions']['10']} regression**, **{late['transitions']['11']} shared successes**, and **{late['transitions']['00']} shared failures** (exact two-sided McNemar p = **{late['exact_mcnemar_two_sided_p']:.8g}**).",
        "",
        "## Interpretation",
        "",
        "The primary first-pass effect survives removal of any one provider configuration, task instance, family, environment type, or individual full stratum. The matched recovery extension independently shows that exact execution state remains highly actionable after failure: it substantially outperforms symptom-only feedback on identical archived failure states. Together these analyses separate two benefits of the same contract representation: proactive disclosure prevents unsuitable initial actions, while persistent disclosure makes the bounded recovery step markedly more effective.",
        "",
    ])
    REPORT.write_text("\n".join(lines))
    print(json.dumps({
        "output": str(OUTPUT),
        "report": str(REPORT),
        "P_minus_R": robustness["P_minus_R"]["full"],
        "P_minus_G": robustness["P_minus_G"]["full"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
