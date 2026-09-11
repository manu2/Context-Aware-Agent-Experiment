#!/usr/bin/env python3
"""Run the frozen AAMAS confirmatory analysis over audited provider cohorts.

The program is deliberately fail-closed: inferential output is produced only when
all three provider audits pass and the complete 288-trajectory matrix is present.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random
from statistics import fmean

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDITS = [
    ROOT / "experiments/09_aamas_contract_bridge/analysis/gemini_e5_complete_audit.json",
    ROOT / "experiments/09_aamas_contract_bridge/analysis/claude_e5_complete_audit.json",
    ROOT / "experiments/09_aamas_contract_bridge/analysis/gpt_e5_complete_audit.json",
]
STRATUM = ("model", "family", "instance", "environment")
CONDITIONS = ("P", "R", "G")
REPETITIONS = 4
PERMUTATIONS = 100_000
BOOTSTRAPS = 20_000
PERMUTATION_SEED = 20260924
BOOTSTRAP_SEED = 20260925


def wilson(successes: int, total: int) -> list[float]:
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [center - margin, center + margin]


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def row_key(row: dict, fields: tuple[str, ...] = STRATUM) -> tuple[str, ...]:
    return tuple(row[field] for field in fields)


def validate_and_load(paths: list[Path]) -> list[dict]:
    if len(paths) != 3:
        raise ValueError("exactly three provider audits are required")
    rows: list[dict] = []
    models: set[str] = set()
    identifiers: set[str] = set()
    for path in paths:
        payload = json.loads(path.read_text())
        if not payload.get("passed") or payload.get("complete") != payload.get("scheduled"):
            raise ValueError(f"audit is incomplete or failed: {path}")
        if payload.get("integrity_issues") or payload.get("incomplete"):
            raise ValueError(f"audit contains unresolved evidence: {path}")
        model = payload["model"]
        if model in models:
            raise ValueError(f"duplicate model audit: {model}")
        models.add(model)
        for source in payload["rows"]:
            row = dict(source)
            row["model"] = model
            identifier = row["scheduled_trajectory_id"]
            if identifier in identifiers:
                raise ValueError(f"duplicate scheduled trajectory: {identifier}")
            identifiers.add(identifier)
            if len(row.get("attempts", [])) != row.get("attempt_count"):
                raise ValueError(f"missing compact attempt evidence: {identifier}")
            rows.append(row)
    if len(rows) != 288:
        raise ValueError(f"expected 288 trajectories, found {len(rows)}")
    cells = Counter(row_key(row) + (row["condition"],) for row in rows)
    if len(cells) != 72 or any(count != REPETITIONS for count in cells.values()):
        raise ValueError("matrix is not balanced at four repetitions per frozen cell")
    return rows


def binary_breakdowns(rows: list[dict]) -> dict:
    output = {}
    groupings = {
        "overall": (), "model": ("model",), "family": ("family",),
        "instance": ("family", "instance"), "environment": ("environment",),
        "model_family": ("model", "family"),
        "model_environment": ("model", "environment"),
        "family_environment": ("family", "environment"),
        "full_stratum": STRATUM,
    }
    for name, fields in groupings.items():
        grouped: dict[tuple, list[dict]] = defaultdict(list)
        for row in rows:
            grouped[row_key(row, fields) + (row["condition"],)].append(row)
        entries = []
        for key in sorted(grouped, key=lambda item: item[:-1] + (CONDITIONS.index(item[-1]),)):
            subset = grouped[key]
            first = sum(row["first_pass_suitable"] for row in subset)
            final = sum(row["final_suitable"] for row in subset)
            entries.append({
                **{field: key[index] for index, field in enumerate(fields)},
                "condition": key[-1], "n": len(subset),
                "first_pass_suitable": first,
                "first_pass_rate": first / len(subset),
                "first_pass_wilson_95": wilson(first, len(subset)),
                "final_suitable": final, "final_rate": final / len(subset),
                "final_wilson_95": wilson(final, len(subset)),
                "provider_calls": sum(row["attempt_count"] for row in subset),
                "provider_tokens": sum(row["provider_tokens"] for row in subset),
                "estimated_cost_usd": sum(row["estimated_cost_usd"] for row in subset),
            })
        output[name] = entries
    return output


def equal_stratum_risk_difference(rows: list[dict], comparison: str, outcome: str) -> float:
    grouped: dict[tuple, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row_key(row)][row["condition"]].append(bool(row[outcome]))
    differences = []
    for cells in grouped.values():
        differences.append(fmean(cells["P"]) - fmean(cells[comparison]))
    return fmean(differences)


def primary_randomization(rows: list[dict], permutations: int = PERMUTATIONS) -> dict:
    grouped: dict[tuple, list[bool]] = defaultdict(list)
    for row in rows:
        grouped[row_key(row)].append(bool(row["first_pass_suitable"]))
    strata = list(grouped.values())
    observed = {
        "P_minus_R": equal_stratum_risk_difference(rows, "R", "first_pass_suitable"),
        "P_minus_G": equal_stratum_risk_difference(rows, "G", "first_pass_suitable"),
    }
    extremes = {contrast: 0 for contrast in observed}
    rng = random.Random(PERMUTATION_SEED)
    for _ in range(permutations):
        sums = {condition: 0.0 for condition in CONDITIONS}
        for outcomes in strata:
            shuffled = list(outcomes)
            rng.shuffle(shuffled)
            for index, condition in enumerate(CONDITIONS):
                start = index * REPETITIONS
                sums[condition] += sum(shuffled[start:start + REPETITIONS]) / REPETITIONS
        permuted = {
            "P_minus_R": (sums["P"] - sums["R"]) / len(strata),
            "P_minus_G": (sums["P"] - sums["G"]) / len(strata),
        }
        for contrast, statistic in permuted.items():
            if abs(statistic) >= abs(observed[contrast]) - 1e-15:
                extremes[contrast] += 1
    raw_p = {contrast: (extremes[contrast] + 1) / (permutations + 1) for contrast in observed}
    ordered = sorted(raw_p, key=raw_p.get)
    adjusted = {}
    running = 0.0
    for rank, contrast in enumerate(ordered):
        running = max(running, min(1.0, raw_p[contrast] * (len(ordered) - rank)))
        adjusted[contrast] = running
    return {
        "estimand": "equal-stratum-weighted first-pass suitability risk difference",
        "strata": len(strata), "permutations": permutations,
        "seed": PERMUTATION_SEED, "observed": observed,
        "two_sided_randomization_p": raw_p, "holm_adjusted_p": adjusted,
    }


def metric(row: dict, name: str) -> float | None:
    if name.startswith("first_"):
        return row["attempts"][0].get(name.removeprefix("first_"))
    if name.startswith("final_"):
        return row["attempts"][-1].get(name.removeprefix("final_"))
    return row.get(name)


CONTINUOUS_METRICS = (
    "first_program_time_seconds", "final_program_time_seconds",
    "first_memory_peak_bytes", "final_memory_peak_bytes",
    "first_memory_exceedance_bytes", "final_memory_exceedance_bytes",
    "end_to_end_seconds", "provider_tokens", "attempt_count", "estimated_cost_usd",
)


def continuous_contrasts(rows: list[dict], bootstraps: int = BOOTSTRAPS) -> dict:
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        cells[row_key(row) + (row["condition"],)].append(row)
    strata = sorted({key[:-1] for key in cells})

    def estimates(sampled: dict[tuple, list[dict]]) -> dict[str, dict[str, float | int]]:
        result = {}
        for name in CONTINUOUS_METRICS:
            differences = {"P_minus_R": [], "P_minus_G": []}
            used = {"P_minus_R": 0, "P_minus_G": 0}
            for stratum in strata:
                means = {}
                for condition in CONDITIONS:
                    values = [metric(row, name) for row in sampled[stratum + (condition,)]]
                    observed_values = [float(value) for value in values if value is not None]
                    means[condition] = fmean(observed_values) if observed_values else None
                for comparison in ("R", "G"):
                    contrast = f"P_minus_{comparison}"
                    if means["P"] is not None and means[comparison] is not None:
                        differences[contrast].append(means["P"] - means[comparison])
                        used[contrast] += 1
            result[name] = {
                contrast: fmean(values) for contrast, values in differences.items() if values
            }
            result[name]["strata_used_P_minus_R"] = used["P_minus_R"]
            result[name]["strata_used_P_minus_G"] = used["P_minus_G"]
        return result

    observed = estimates(cells)
    distributions = {
        name: {"P_minus_R": [], "P_minus_G": []} for name in CONTINUOUS_METRICS
    }
    rng = random.Random(BOOTSTRAP_SEED)
    for _ in range(bootstraps):
        sampled = {
            key: [rng.choice(values) for _ in range(len(values))]
            for key, values in cells.items()
        }
        replicate = estimates(sampled)
        for name in CONTINUOUS_METRICS:
            for contrast in ("P_minus_R", "P_minus_G"):
                value = replicate[name].get(contrast)
                if value is not None:
                    distributions[name][contrast].append(value)
    output = {}
    for name in CONTINUOUS_METRICS:
        output[name] = dict(observed[name])
        output[name]["bootstrap_95"] = {
            contrast: [percentile(values, 0.025), percentile(values, 0.975)]
            for contrast, values in distributions[name].items()
        }
    return {"bootstraps": bootstraps, "seed": BOOTSTRAP_SEED, "metrics": output}


def behavioral_summaries(rows: list[dict]) -> dict:
    failures = {"first": Counter(), "final": Counter()}
    strategies: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        first, final = row["attempts"][0], row["attempts"][-1]
        if first["failure_type"]:
            failures["first"][first["failure_type"]] += 1
        if final["failure_type"]:
            failures["final"][final["failure_type"]] += 1
        key = "/".join((row["model"], row["family"], row["environment"], row["condition"]))
        strategies[key][first["strategy"]["primary_strategy"]] += 1
    return {
        "failure_counts": {stage: dict(counts) for stage, counts in failures.items()},
        "first_attempt_strategy_counts": {key: dict(counts) for key, counts in sorted(strategies.items())},
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# AAMAS confirmatory analysis", "",
        "This report is generated only after all three provider cohorts pass the frozen evidence audit.", "",
        "## Co-primary outcomes", "",
        "| Contrast | Stratified risk difference | Raw randomization p | Holm-adjusted p |",
        "|---|---:|---:|---:|",
    ]
    primary = payload["primary_analysis"]
    for contrast in ("P_minus_R", "P_minus_G"):
        lines.append(
            f"| {contrast.replace('_', ' ')} | {primary['observed'][contrast]:.3f} | "
            f"{primary['two_sided_randomization_p'][contrast]:.6g} | "
            f"{primary['holm_adjusted_p'][contrast]:.6g} |"
        )
    lines += ["", "## Condition outcomes", "",
              "| Condition | N | First-pass suitable | Final suitable | Calls | Tokens | Estimated cost |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for item in payload["binary_breakdowns"]["overall"]:
        lines.append(
            f"| {item['condition']} | {item['n']} | {item['first_pass_suitable']}/{item['n']} "
            f"({item['first_pass_rate']:.1%}) | {item['final_suitable']}/{item['n']} "
            f"({item['final_rate']:.1%}) | {item['provider_calls']} | {item['provider_tokens']} | "
            f"${item['estimated_cost_usd']:.3f} |"
        )
    lines += ["", "All task-, environment-, instance-, model-, failure-, strategy-, and bootstrap results are preserved in the companion JSON.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="append", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/09_aamas_contract_bridge/analysis/confirmatory_analysis.json")
    parser.add_argument("--report", type=Path, default=ROOT / "docs/24_aamas_confirmatory_results.md")
    parser.add_argument("--permutations", type=int, default=PERMUTATIONS)
    parser.add_argument("--bootstraps", type=int, default=BOOTSTRAPS)
    args = parser.parse_args()
    paths = [path if path.is_absolute() else ROOT / path for path in (args.audit or DEFAULT_AUDITS)]
    rows = validate_and_load(paths)
    payload = {
        "schema_version": "aamas-confirmatory-analysis/v1.0",
        "frozen_analysis_plan": "experiments/09_aamas_contract_bridge/protocol/CONFIRMATORY_ANALYSIS_PLAN.md",
        "source_audits": [
            str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
            for path in paths
        ],
        "trajectory_count": len(rows),
        "binary_breakdowns": binary_breakdowns(rows),
        "primary_analysis": primary_randomization(rows, args.permutations),
        "continuous_analysis": continuous_contrasts(rows, args.bootstraps),
        "behavioral_analysis": behavioral_summaries(rows),
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    report = args.report if args.report.is_absolute() else ROOT / args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    report.write_text(render_markdown(payload))
    print(json.dumps({"trajectory_count": len(rows), "primary_analysis": payload["primary_analysis"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
