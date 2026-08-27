#!/usr/bin/env python3
"""Fail closed if the fresh evidence package diverges from archived artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECT = ROOT / "experiments/06_replication/raw"
SWEEP = ROOT / "experiments/08_96mb_cgroup_pilot/raw"
AUDIT = ROOT / "experiments/06_replication/audit/fresh_code_transformation_audit.json"
FIGURES = [ROOT / "paper/figures/fresh_128mb_paired_maxrss.pdf", ROOT / "paper/figures/fresh_boundary_sensitivity_maxrss.pdf"]
DATASET = ROOT / "data/vectors.npy"
DATASET_SHA256 = "199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def direct_records(model: str, prefix: str, indices: list[int]) -> list[tuple[dict, dict]]:
    records = []
    for index in indices:
        a = load(DIRECT / model / f"{prefix}{index:02d}_A/metadata.json")["profile"]
        d = load(DIRECT / model / f"{prefix}{index:02d}_D/metadata.json")["profile"]
        records.append((a, d))
    return records


def sweep_records(model: str, prefix: str, indices: list[int]) -> list[dict]:
    return [load(SWEEP / model / f"{prefix}{index:02d}_D/local_observed_rss_profile.json")["profile"] for index in indices]


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify fresh evidence artifacts; optionally audit a manuscript text file."
    )
    parser.add_argument(
        "--manuscript",
        type=Path,
        help="optional Markdown manuscript whose displayed rows and boundary statements are checked",
    )
    args = parser.parse_args()
    groups = {
        "claude-opus-5": (direct_records("claude-opus-5", "opus_rep", [2, 3, 4, 5, 6]), 256.48, 107.82, 4, 4),
        "gpt-5.6-sol": (direct_records("gpt-5.6-sol", "gpt_rep", [1, 2, 3, 4, 5]), 118.63, 64.61, 4, 5),
        "gemini-3.7-flash": (direct_records("gemini-3.7-flash", "gemini_rep", [1, 2, 3, 4, 5]), 452.36, 158.16, 5, 5),
    }
    for model, (pairs, expected_a, expected_d, expected_lower, denominator) in groups.items():
        a_executable = [a["maxrss_mb"] for a, _ in pairs if a["correct"]]
        d_values = [d["maxrss_mb"] for _, d in pairs]
        executable = [(a, d) for a, d in pairs if a["correct"]]
        require(round(mean(a_executable), 2) == expected_a, f"{model} blind mean is {expected_a:.2f} MB")
        require(round(mean(d_values), 2) == expected_d, f"{model} disclosed mean is {expected_d:.2f} MB")
        require(sum(d["maxrss_mb"] < a["maxrss_mb"] for a, d in executable) == expected_lower, f"{model} has {expected_lower}/{denominator} lower-RSS executable pairs")

    sweep = {
        "GPT": (sweep_records("gpt-5.6-sol", "gpt96_rep", [1, 2, 3, 4, 5]), 60.88, 5),
        "Claude": (sweep_records("claude-opus-5", "opus96_rep", [1, 2, 4, 6, 7]), 87.57, 4),
        "Gemini": (sweep_records("gemini-3.7-flash", "gemini96_rep", [1, 2, 3, 4, 5]), 118.46, 3),
    }
    for label, (records, expected_mean, expected_under_96) in sweep.items():
        require(all(record["correct"] and record["wall_sec"] < 10 for record in records), f"{label} retained 96 MB programs are correct and under 10 s")
        require(round(mean([record["maxrss_mb"] for record in records]), 2) == expected_mean, f"{label} 96 MB mean is {expected_mean:.2f} MB")
        require(sum(record["maxrss_mb"] <= 96 for record in records) == expected_under_96, f"{label} has {expected_under_96}/5 observed <=96 MB")

    audit = load(AUDIT)
    require(len(audit["records"]) == 45, "code audit contains 45 retained source records")
    require(len([r for r in audit["records"] if r["cohort"] == "fresh_128mb_direct_api"]) == 30, "code audit contains 30 direct-API source records")
    require(len([r for r in audit["records"] if r["cohort"] == "fresh_96mb_local_sweep"]) == 15, "code audit contains 15 retained 96 MB source records")
    for record in audit["records"]:
        source = ROOT / record["source_path"]
        require(source.exists() and sha256(source) == record["source_sha256"], f"audit digest matches {record['trial_id']}")
    require(DATASET.exists() and sha256(DATASET) == DATASET_SHA256, "deterministic dataset hash matches manifest")
    manifest = load(ROOT / "experiments/08_96mb_cgroup_pilot/RUN_MANIFEST.json")
    statuses = {entry["trial_id"]: entry.get("status") for entry in manifest["executions"]}
    require(statuses["opus96_rep03_D"] == "response_invalid_empty", "manifest labels empty Claude response invalid")
    require(statuses["opus96_rep05_D"] == "response_invalid_truncated", "manifest labels truncated Claude response invalid")
    require(statuses["opus96_rep06_D"] == "replacement_for_truncated_opus96_rep05_D", "manifest retains Claude truncated-response replacement")
    require(statuses["opus96_rep07_D"] == "replacement_for_empty_opus96_rep03_D", "manifest retains Claude empty-response replacement")
    require(all(path.exists() and path.stat().st_size > 1000 for path in FIGURES), "both checked-in PDF figures exist")

    if args.manuscript is None:
        print("SKIP manuscript text checks (pass --manuscript PATH for a local draft audit)")
        return

    manuscript = args.manuscript.resolve()
    require(manuscript.exists(), f"manuscript exists: {manuscript}")
    paper = manuscript.read_text(encoding="utf-8")
    expected_table_rows = (
        "| `claude-opus-5` | 256.48 MB* | 107.82 MB | lower 4/4 | 0.9109 s* | 0.3612 s | 0/5 -> 5/5 |",
        "| `gpt-5.6-sol` | 118.63 MB | 64.61 MB | lower 4/5; higher 1/5 | 0.5507 s | 0.3282 s | 4/5 -> 5/5 |",
        "| `gemini-3.7-flash` | 452.36 MB | 158.16 MB | lower 5/5 | 1.0994 s | 0.3561 s | 0/5 -> 2/5 |",
        "| `gpt-5.6-sol` | 1/5 | 5/5 | 60.88 MB | 5/5 | 0.3582 s |",
        "| `claude-opus-5` | 0/5 | 0/5 | 87.57 MB | 4/5 | 0.3802 s |",
        "| `gemini-3.7-flash` | 0/5 | 0/5 | 118.46 MB | 3/5 | 0.3985 s |",
    )
    for row in expected_table_rows:
        require(row in paper, f"manuscript table row matches archived result: {row.split('|')[1].strip()}")
    normalized_paper = " ".join(paper.split())
    required_claims = (
        "13 of 14 executable",
        "Mean wall time also falls in every cohort",
        "All 15 retained executable 96 MB programs are numerically correct",
        "independently generated",
        "model-dependent",
    )
    for statement in required_claims:
        require(" ".join(statement.split()) in normalized_paper, f"manuscript contains evidence-boundary claim: {statement!r}")


if __name__ == "__main__":
    main()
