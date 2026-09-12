#!/usr/bin/env python3
"""Audit and analyze one matched late-disclosure provider cohort."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))
from run_aamas_late_disclosure import branch_prompt, load_source


def exact_mcnemar_two_sided(improved: int, regressed: int) -> float:
    discordant = improved + regressed
    if not discordant:
        return 1.0
    tail = sum(math.comb(discordant, k) for k in range(min(improved, regressed) + 1)) / (2 ** discordant)
    return min(1.0, 2 * tail)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    protocol = ROOT / "experiments/09_aamas_contract_bridge/protocol"
    manifest = json.loads((protocol / args.manifest).read_text())
    source_root = ROOT / "experiments/09_aamas_contract_bridge" / manifest["source_archive_subdir"]
    output_root = ROOT / "experiments/09_aamas_contract_bridge" / manifest["archive_subdir"]
    required = {"events.jsonl", "program.py", "prompt.txt", "provider_response.json",
                "raw_response.txt", "strategy.json", "summary.json", "trajectory_manifest.json"}
    issues, rows = [], []
    prefix = manifest["run_id_prefix"]
    expected_dirs = {f"{prefix}-{index:03d}-{branch}" for index, (_, branch) in enumerate(manifest["execution_order"], 1)}
    actual_dirs = {p.name for p in output_root.glob(prefix + "-*") if p.is_dir()}
    if actual_dirs != expected_dirs:
        issues.append({"kind": "directory_set", "missing": sorted(expected_dirs - actual_dirs),
                       "extra": sorted(actual_dirs - expected_dirs)})
    for index, (source_id, branch) in enumerate(manifest["execution_order"], 1):
        directory = output_root / f"{prefix}-{index:03d}-{branch}"
        missing = sorted(required - {p.name for p in directory.iterdir()}) if directory.exists() else sorted(required)
        if missing:
            issues.append({"kind": "missing_artifacts", "trajectory": directory.name, "files": missing})
            continue
        late = json.loads((directory / "summary.json").read_text())
        branch_manifest = json.loads((directory / "trajectory_manifest.json").read_text())
        source = load_source(source_root, source_id)
        source_summary = source["summary"]
        source_program_hash = hashlib.sha256((source["directory"] / "attempt_1_program.py").read_bytes()).hexdigest()
        source_observation_hash = hashlib.sha256(
            json.dumps(source["observation"].to_dict(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if source_program_hash != branch_manifest["source_first_attempt_program_sha256"]:
            issues.append({"kind": "source_program_hash", "trajectory": directory.name})
        if source_observation_hash != branch_manifest["source_first_attempt_execution_sha256"]:
            issues.append({"kind": "source_observation_hash", "trajectory": directory.name})
        if (directory / "prompt.txt").read_text() != branch_prompt(source, branch):
            issues.append({"kind": "prompt_reconstruction", "trajectory": directory.name})
        events = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()]
        if [event["kind"] for event in events] != ["matched_recovery_branch", "generation", "execution", "score"]:
            issues.append({"kind": "event_sequence", "trajectory": directory.name})
        old_suitable = bool(source_summary["attempts"][-1]["score"]["suitable"])
        new_suitable = bool(late["score"]["suitable"])
        canonical_source = source["snapshot"].get("infrastructure_replacement_for", source_id)
        rows.append({
            "trajectory_id": directory.name, "source_archive_id": source_id,
            "canonical_source_trajectory_id": canonical_source,
            "family": late["family"], "instance": late["instance"],
            "environment": late["environment"], "model": late["model"],
            "archived_R_final_suitable": old_suitable, "late_L_suitable": new_suitable,
            "transition": f"{int(old_suitable)}{int(new_suitable)}",
            "L_score": late["score"], "L_execution": late["execution"],
            "L_strategy": late["strategy"], "L_generation": late["generation"],
        })
    ledger = json.loads((output_root / manifest["budget_ledger_file"]).read_text())
    if ledger["calls"] != len(manifest["execution_order"]):
        issues.append({"kind": "ledger_call_count", "observed": ledger["calls"]})
    if any(entry["status"] != "complete" for entry in ledger["entries"]):
        issues.append({"kind": "ledger_noncomplete_entry"})
    transitions = Counter(row["transition"] for row in rows)
    strata = defaultdict(lambda: {"n": 0, "R": 0, "L": 0})
    for row in rows:
        key = f"{row['family']}|{row['environment']}"
        strata[key]["n"] += 1
        strata[key]["R"] += row["archived_R_final_suitable"]
        strata[key]["L"] += row["late_L_suitable"]
    model_name = rows[0]["model"] if rows else manifest["model"]["id"]
    analysis = {
        "schema_version": "aamas-late-disclosure-analysis/v1.0",
        "manifest": args.manifest, "model": model_name,
        "nonpooled_canary_excluded": bool(manifest.get("nonpooled_canary_excluded", False)),
        "passed": not issues, "integrity_issues": issues, "n": len(rows),
        "archived_R_final_suitable": sum(row["archived_R_final_suitable"] for row in rows),
        "late_L_suitable": sum(row["late_L_suitable"] for row in rows),
        "transitions": {key: transitions.get(key, 0) for key in ("00", "01", "10", "11")},
        "exact_mcnemar_two_sided_p": exact_mcnemar_two_sided(transitions.get("01", 0), transitions.get("10", 0)),
        "strata": dict(sorted(strata.items())), "provider_calls": ledger["calls"],
        "estimated_cost_usd": ledger["estimated_cost_usd"], "rows": rows,
    }
    analysis_path = ROOT / args.analysis
    analysis_path.parent.mkdir(parents=True, exist_ok=True)
    analysis_path.write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    lines = [
        f"# {model_name} late-disclosure recovery extension", "",
        "> This separately frozen extension branches from the same archived R first-attempt failures. Any declared development canary is excluded.", "",
        f"- Integrity audit: **{'PASS' if analysis['passed'] else 'FAIL'}**",
        f"- Matched failure states: **{analysis['n']}**",
        f"- Archived symptom-only recovery suitable: **{analysis['archived_R_final_suitable']}/{analysis['n']}**",
        f"- Late exact-contract recovery suitable: **{analysis['late_L_suitable']}/{analysis['n']}**",
        f"- Transitions: R-fail/L-fail {transitions.get('00',0)}, R-fail/L-success {transitions.get('01',0)}, R-success/L-fail {transitions.get('10',0)}, both suitable {transitions.get('11',0)}",
        f"- Descriptive exact matched McNemar p-value: **{analysis['exact_mcnemar_two_sided_p']:.8g}**",
        f"- Provider calls/cost: **{ledger['calls']} / ${ledger['estimated_cost_usd']:.6f}**", "",
        "## Stratified outcomes", "", "| Family | Environment | N | Archived R | Late L |", "|---|---|---:|---:|---:|",
    ]
    for key, value in analysis["strata"].items():
        family, environment = key.split("|")
        lines.append(f"| {family} | {environment} | {value['n']} | {value['R']}/{value['n']} | {value['L']}/{value['n']} |")
    lines.extend(["", "## Interpretation", "",
                  f"For {model_name}, the exact execution contract supplied at recovery converted {transitions.get('01',0)} failure states that remained unsuitable under archived symptom-only recovery. {transitions.get('10',0)} archived R successes regressed, {transitions.get('11',0)} states were suitable under both recovery prompts, and {transitions.get('00',0)} remained unsuitable under both. This provider cohort measures the added value of explicit boundary disclosure over authentic failure evidence on identical archived failure states.", ""])
    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines))
    print(json.dumps({key: analysis[key] for key in ("passed", "n", "archived_R_final_suitable", "late_L_suitable", "transitions", "exact_mcnemar_two_sided_p", "estimated_cost_usd")}, indent=2))
    return 0 if analysis["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
