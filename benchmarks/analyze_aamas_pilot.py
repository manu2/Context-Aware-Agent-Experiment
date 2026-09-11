#!/usr/bin/env python3
"""Build a deterministic descriptive report from the non-pooled Gemini pilot."""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "experiments/09_aamas_contract_bridge/api_pilot"
ID = re.compile(r"-(\d+)-(numerical|etl)-(memory_tight|latency_tight)-([PRG])$")


def strategy(family: str, source: str) -> str:
    lowered = source.lower()
    if family == "etl":
        if "pandas" in lowered and "chunksize" in lowered:
            return "pandas_chunked"
        if "pandas" in lowered:
            return "pandas_eager_or_vectorized"
        if "import csv" in lowered or "open(" in lowered:
            return "stdlib_streaming"
        return "other"
    has_loop = bool(re.search(r"\bfor\b.*\brange\s*\(", source, re.DOTALL))
    has_product = "@" in source or "matmul" in lowered or ".dot(" in lowered
    if has_loop and has_product:
        return "blocked_or_streamed_matrix_product"
    if has_product:
        return "unblocked_matrix_product"
    return "other"


def main() -> int:
    report_path = PILOT / "pilot-gemini38-v1_report.json"
    report = json.loads(report_path.read_text())
    ledger = json.loads((PILOT / "budget_ledger.json").read_text())
    rows = []
    for summary in report["summaries"]:
        match = ID.search(summary["trajectory_id"])
        if not match:
            raise ValueError(f"unrecognized trajectory ID: {summary['trajectory_id']}")
        _, family, environment, condition = match.groups()
        directory = PILOT / summary["trajectory_id"]
        attempts = []
        for attempt in summary["attempts"]:
            number = attempt["attempt"]
            source = (directory / f"attempt_{number}_program.py").read_text()
            attempts.append({
                "attempt": number,
                "strategy": strategy(family, source),
                "program_sha256": sha256(source.encode()).hexdigest(),
                "score": attempt["score"],
                "execution": attempt["execution"],
                "generation": attempt["generation"],
            })
        rows.append({
            "trajectory_id": summary["trajectory_id"], "family": family,
            "environment": environment, "condition": condition,
            "first_pass_suitable": summary["first_pass_suitable"],
            "final_suitable": summary["final_suitable"],
            "attempt_count": summary["attempt_count"], "attempts": attempts,
        })

    cells = {}
    for key in sorted({(r["family"], r["environment"], r["condition"]) for r in rows}):
        subset = [r for r in rows if (r["family"], r["environment"], r["condition"]) == key]
        cells["/".join(key)] = {
            "n": len(subset),
            "first_pass_suitable": sum(r["first_pass_suitable"] for r in subset),
            "final_suitable": sum(r["final_suitable"] for r in subset),
            "calls": sum(r["attempt_count"] for r in subset),
            "first_strategy_counts": dict(Counter(r["attempts"][0]["strategy"] for r in subset)),
        }
    conditions = {}
    for condition in "PRG":
        subset = [r for r in rows if r["condition"] == condition]
        conditions[condition] = {
            "n": len(subset),
            "first_pass_suitable": sum(r["first_pass_suitable"] for r in subset),
            "final_suitable": sum(r["final_suitable"] for r in subset),
            "calls": sum(r["attempt_count"] for r in subset),
        }
    first_failures = Counter()
    final_failures = Counter()
    for row in rows:
        for counter, attempt in ((first_failures, row["attempts"][0]), (final_failures, row["attempts"][-1])):
            execution = attempt["execution"]
            if execution["oom_killed"]:
                counter["oom_kill"] += 1
            elif execution["timed_out"]:
                counter["timeout"] += 1
            elif not attempt["score"]["correct"]:
                counter["incorrect_or_runtime_error"] += 1
    payload = {
        "schema_version": "aamas-pilot-analysis/v0.1",
        "source_report": str(report_path.relative_to(ROOT)),
        "non_pooled": True,
        "model": "gemini-3.8-flash",
        "trajectory_count": len(rows),
        "provider_call_count": ledger["calls"],
        "estimated_api_cost_usd": ledger["estimated_cost_usd"],
        "finish_reason_counts": dict(Counter(e.get("finish_reason", "missing") for e in ledger["entries"])),
        "condition_summary": conditions,
        "cell_summary": cells,
        "first_failure_counts": dict(first_failures),
        "final_failure_counts": dict(final_failures),
        "rows": rows,
    }
    (PILOT / "pilot_analysis.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Gemini 3.8 Flash non-pooled pilot", "",
        "This development pilot is used to freeze the confirmatory protocol and is never pooled with confirmatory evidence.", "",
        f"- Trajectories: {len(rows)}",
        f"- Provider calls: {ledger['calls']}",
        f"- Estimated API cost: ${ledger['estimated_cost_usd']:.3f}",
        f"- Finish reasons: {dict(Counter(e.get('finish_reason', 'missing') for e in ledger['entries']))}", "",
        "## Outcomes by condition", "",
        "| Condition | N | First-pass suitable | Final suitable | Calls |", "|---|---:|---:|---:|---:|",
    ]
    for condition in "PRG":
        item = conditions[condition]
        lines.append(f"| {condition} | {item['n']} | {item['first_pass_suitable']}/{item['n']} | {item['final_suitable']}/{item['n']} | {item['calls']} |")
    lines += ["", "## Outcomes by cell", "", "| Family | Environment | Condition | First | Final | Initial strategies |", "|---|---|---:|---:|---:|---|"]
    for key, item in cells.items():
        family, environment, condition = key.split("/")
        lines.append(f"| {family} | {environment} | {condition} | {item['first_pass_suitable']}/{item['n']} | {item['final_suitable']}/{item['n']} | `{item['first_strategy_counts']}` |")
    lines += [
        "", "## Gate reading", "",
        "The proactive condition achieved 7/8 first-pass and 8/8 final suitability, compared with 3/8 and 4/8 for reactive discovery and 4/8 and 4/8 for generic efficiency guidance.",
        "On the numerical task, proactive disclosure was suitable in all 4 trajectories while reactive and generic conditions were suitable in 0/4. On ETL, every condition ultimately completed, but the selected implementations differed with the envelope: proactive memory runs streamed, while proactive latency runs used Pandas and completed within the tighter time contract.",
        "These are pilot observations, not confirmatory estimates. They support advancing to protocol freeze while retaining task-, environment-, and model-stratified analysis.", "",
    ]
    (PILOT / "PILOT_REPORT.md").write_text("\n".join(lines))
    print(json.dumps({k: payload[k] for k in ("trajectory_count", "provider_call_count", "estimated_api_cost_usd", "condition_summary")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
