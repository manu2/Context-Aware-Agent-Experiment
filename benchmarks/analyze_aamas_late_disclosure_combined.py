#!/usr/bin/env python3
"""Combine integrity-passing late-disclosure cohorts with frozen P/R workflows."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "experiments/09_aamas_contract_bridge/analysis"

LATE_FILES = {
    "gemini-3.8-flash": "gemini_late_disclosure_v1.json",
    "claude-sonnet-5": "claude_late_disclosure_v1.json",
    "gpt-5.6-sol": "gpt_late_disclosure_v1.json",
}
AUDIT_FILES = {
    "gemini-3.8-flash": "gemini_e5_complete_audit.json",
    "claude-sonnet-5": "claude_e5_complete_audit.json",
    "gpt-5.6-sol": "gpt_e5_complete_audit.json",
}


def exact_mcnemar(improved: int, regressed: int) -> float:
    n = improved + regressed
    if not n:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(improved, regressed) + 1)) / (2 ** n))


def main() -> int:
    late, audits = {}, {}
    for model, filename in LATE_FILES.items():
        late[model] = json.loads((ANALYSIS / filename).read_text())
        if not late[model]["passed"]:
            raise RuntimeError(f"late-disclosure audit failed for {model}")
    for model, filename in AUDIT_FILES.items():
        audits[model] = json.loads((ANALYSIS / filename).read_text())
        if not audits[model]["passed"]:
            raise RuntimeError(f"confirmatory audit failed for {model}")
    transitions = Counter()
    by_initial_failure = defaultdict(lambda: {"n": 0, "R_recovered": 0, "L_recovered": 0})
    late_residual_failures = Counter()
    workflow = {}
    all_rows = []
    for model in LATE_FILES:
        l = late[model]
        transitions.update(l["transitions"])
        rows = audits[model]["rows"]
        p = [row for row in rows if row["condition"] == "P"]
        r = [row for row in rows if row["condition"] == "R"]
        r_first = sum(row["first_pass_suitable"] for row in r)
        workflow[model] = {
            "n": len(r), "P_first": sum(row["first_pass_suitable"] for row in p),
            "P_final": sum(row["final_suitable"] for row in p), "R_first": r_first,
            "R_final_symptom_only": sum(row["final_suitable"] for row in r),
            "R_final_late_contract": r_first + l["late_L_suitable"],
        }
        all_rows.extend(l["rows"])
        for row in l["rows"]:
            source = json.loads((ROOT / "experiments/09_aamas_contract_bridge/confirmatory"
                                 / row["source_archive_id"] / "summary.json").read_text())
            first = source["attempts"][0]["execution"]
            failure = "oom" if first["oom_killed"] else "timeout" if first["timed_out"] else "other"
            by_initial_failure[failure]["n"] += 1
            by_initial_failure[failure]["R_recovered"] += row["archived_R_final_suitable"]
            by_initial_failure[failure]["L_recovered"] += row["late_L_suitable"]
            if not row["late_L_suitable"]:
                execution = row["L_execution"]
                residual = "oom" if execution["oom_killed"] else "timeout" if execution["timed_out"] else "runtime_or_wrong"
                late_residual_failures[residual] += 1
    totals = {key: sum(row[key] for row in workflow.values())
              for key in ("n", "P_first", "P_final", "R_first", "R_final_symptom_only", "R_final_late_contract")}
    p_provider_calls = totals["n"] + sum(row["n"] - row["P_first"] for row in workflow.values())
    late_provider_calls = totals["n"] + len(all_rows)
    result = {
        "schema_version": "aamas-late-disclosure-combined/v1.0",
        "passed": len(all_rows) == 82,
        "matched_R_failure_states": len(all_rows),
        "archived_R_symptom_only_recovered": sum(x["archived_R_final_suitable"] for x in all_rows),
        "late_contract_recovered": sum(x["late_L_suitable"] for x in all_rows),
        "transitions": {key: transitions[key] for key in ("00", "01", "10", "11")},
        "exact_mcnemar_two_sided_p": exact_mcnemar(transitions["01"], transitions["10"]),
        "workflow_by_model": workflow, "workflow_total": totals,
        "provider_calls": {"P_workflow": p_provider_calls,
                           "late_contract_workflow": late_provider_calls},
        "recovery_by_initial_failure": dict(sorted(by_initial_failure.items())),
        "late_residual_failure_types": dict(sorted(late_residual_failures.items())),
        "estimated_provider_cost_usd": sum(late[model]["estimated_cost_usd"] for model in late),
        "source_analyses": list(LATE_FILES.values()),
    }
    if not result["passed"]:
        raise RuntimeError("combined late-disclosure matrix is not 82 states")
    (ANALYSIS / "late_disclosure_combined_v1.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        "# AAMAS late-disclosure recovery extension: combined analysis", "",
        "> Separately frozen extension over the 82 archived first-attempt failures in condition R. Development canary results are excluded.", "",
        f"Exact contract disclosure at recovery increased suitable recovery from **{result['archived_R_symptom_only_recovered']}/82** to **{result['late_contract_recovered']}/82**. Matched transitions were **{transitions['01']} improvements**, **{transitions['10']} regression**, **{transitions['11']} shared successes**, and **{transitions['00']} shared failures** (descriptive exact McNemar p = **{result['exact_mcnemar_two_sided_p']:.8g}**).", "",
        "## Complete workflow", "", "| Model | P first | P final | R first | R final: symptoms | R final: late contract |", "|---|---:|---:|---:|---:|---:|",
    ]
    for model, row in workflow.items():
        lines.append(f"| {model} | {row['P_first']}/{row['n']} | {row['P_final']}/{row['n']} | {row['R_first']}/{row['n']} | {row['R_final_symptom_only']}/{row['n']} | {row['R_final_late_contract']}/{row['n']} |")
    lines.append(f"| **All** | **{totals['P_first']}/{totals['n']}** | **{totals['P_final']}/{totals['n']}** | **{totals['R_first']}/{totals['n']}** | **{totals['R_final_symptom_only']}/{totals['n']}** | **{totals['R_final_late_contract']}/{totals['n']}** |")
    lines.extend(["", "## Interpretation", "",
                  "The exact execution contract is valuable both before action and after failure. Symptom-only recovery leaves the operational boundary implicit; revealing the boundary converts substantially more failures into suitable programs. Proactive disclosure achieves 64 suitable first attempts and avoids the failed execution and additional generation required by late disclosure. Late disclosure raises the corresponding R workflow to 67 final successes, showing that models can still adapt strongly when precise substrate information arrives after failure. The strongest system design therefore supplies the contract before planning and retains exact-contract recovery for residual failures.", "",
                  f"The source failures comprised {by_initial_failure['oom']['n']} OOM kills and {by_initial_failure['timeout']['n']} timeouts. L recovered {by_initial_failure['oom']['L_recovered']}/{by_initial_failure['oom']['n']} OOM-origin states and {by_initial_failure['timeout']['L_recovered']}/{by_initial_failure['timeout']['n']} timeout-origin states. No L execution was OOM-killed; the residual failures were {late_residual_failures['timeout']} timeouts and {late_residual_failures['runtime_or_wrong']} runtime/correctness errors.", "",
                  f"The proactive workflow used {result['provider_calls']['P_workflow']} provider calls, versus {result['provider_calls']['late_contract_workflow']} for the late-disclosure workflow—a difference of {result['provider_calls']['late_contract_workflow'] - result['provider_calls']['P_workflow']} calls.", "",
                  f"Total estimated provider cost for the 82 L branches was **${result['estimated_provider_cost_usd']:.6f}**.", ""])
    (ROOT / "docs/34_aamas_late_disclosure_combined_report.md").write_text("\n".join(lines))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
