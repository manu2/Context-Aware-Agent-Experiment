#!/usr/bin/env python3
"""Build a source-linked audit of every retained fresh generated program.

The audit deliberately records observable source features and supporting line
snippets instead of inferring an algorithmic intention.  It is an aid to
reviewers, not a substitute for the archived generated scripts.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DIRECT_ROOT = ROOT / "experiments/06_replication/raw"
SWEEP_ROOT = ROOT / "experiments/08_96mb_cgroup_pilot/raw"
AUDIT_JSON = ROOT / "experiments/06_replication/audit/fresh_code_transformation_audit.json"
AUDIT_MARKDOWN = ROOT / "docs/13_fresh_code_transformation_audit.md"

DIRECT_IDS = {
    "claude-opus-5": [f"opus_rep{i:02d}_{condition}" for i in range(2, 7) for condition in ("A", "D")],
    "gpt-5.6-sol": [f"gpt_rep{i:02d}_{condition}" for i in range(1, 6) for condition in ("A", "D")],
    "gemini-3.7-flash": [f"gemini_rep{i:02d}_{condition}" for i in range(1, 6) for condition in ("A", "D")],
}
SWEEP_IDS = {
    "claude-opus-5": [f"opus96_rep{i:02d}_D" for i in (1, 2, 4, 6, 7)],
    "gpt-5.6-sol": [f"gpt96_rep{i:02d}_D" for i in range(1, 6)],
    "gemini-3.7-flash": [f"gemini96_rep{i:02d}_D" for i in range(1, 6)],
}


def source_lines(source: str, patterns: list[str]) -> list[dict[str, Any]]:
    """Return a small, traceable set of matching source lines."""
    matches: list[dict[str, Any]] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in patterns):
            matches.append({"line": line_number, "text": line.strip()[:220]})
    return matches[:8]


def block_assignments(source: str) -> list[dict[str, Any]]:
    pattern = r"^\s*(?:[A-Za-z_][A-Za-z0-9_]*_)?(?:block|batch|chunk|tile|bs|bsize)[A-Za-z0-9_]*\s*=.*$"
    return source_lines(source, [pattern])


def ast_counts(source: str) -> dict[str, int | None]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {"for_loops": None, "while_loops": None, "max_for_nesting": None}

    max_depth = 0

    def visit(node: ast.AST, depth: int = 0) -> None:
        nonlocal max_depth
        next_depth = depth + 1 if isinstance(node, (ast.For, ast.AsyncFor)) else depth
        max_depth = max(max_depth, next_depth)
        for child in ast.iter_child_nodes(node):
            visit(child, next_depth)

    visit(tree)
    return {
        "for_loops": sum(isinstance(node, (ast.For, ast.AsyncFor)) for node in ast.walk(tree)),
        "while_loops": sum(isinstance(node, ast.While) for node in ast.walk(tree)),
        "max_for_nesting": max_depth,
    }


def input_mode(source: str) -> tuple[str, list[dict[str, Any]]]:
    evidence = source_lines(source, [r"np\.load\(", r"mmap_mode\s*="])
    if re.search(r"mmap_mode\s*=", source):
        return "numpy_mmap", evidence
    if re.search(r"np\.load\(", source):
        return "numpy_load", evidence
    return "not_detected", evidence


def audit_program(model: str, trial_id: str, cohort: str, directory: Path) -> dict[str, Any]:
    source_path = directory / "script.py"
    source = source_path.read_text(encoding="utf-8") if source_path.exists() else ""
    metadata_name = "metadata.json" if cohort == "fresh_128mb_direct_api" else "generation_metadata.json"
    metadata_path = directory / metadata_name
    profile_path = directory / ("metadata.json" if cohort == "fresh_128mb_direct_api" else "local_observed_rss_profile.json")
    metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
    profile_root = json.loads(profile_path.read_text()) if profile_path.exists() else {}
    profile = profile_root.get("profile", {})
    mode, load_evidence = input_mode(source)

    precision_evidence = source_lines(source, [r"float32", r"float64", r"np\.single", r"np\.double"])
    buffer_evidence = source_lines(source, [r"\bout\s*=", r"np\.matmul\(.*out\s*=", r"\.fill\("])
    symmetry_evidence = source_lines(source, [r"triu|tril|upper.triangle|lower.triangle", r"\*\s*2(?:\.0)?\b"])
    blocking_evidence = block_assignments(source) + source_lines(source, [r"range\([^\n]*(?:block|batch|chunk|tile|bs)"])
    matmul_evidence = source_lines(source, [r"@", r"np\.matmul", r"\.dot\("])

    source_valid = bool(source) and ast_counts(source)["for_loops"] is not None
    return {
        "cohort": cohort,
        "model_configured_id": model,
        "trial_id": trial_id,
        "condition": metadata.get("condition") or metadata.get("condition", "unknown"),
        "source_path": str(source_path.relative_to(ROOT)),
        "source_sha256": __import__("hashlib").sha256(source.encode()).hexdigest() if source else None,
        "source_parseable_python": source_valid,
        "measurement": (
            "macOS isolated-child RUSAGE_CHILDREN observed MaxRSS; not cgroup enforcement"
            if cohort == "fresh_96mb_local_sweep"
            else "macOS child-process MaxRSS profile recorded in trial metadata; not cgroup enforcement"
        ),
        "execution": {
            "correct": profile.get("correct"),
            "exit_code": profile.get("exit_code"),
            "timed_out": profile.get("timed_out"),
            "maxrss_mb": profile.get("maxrss_mb"),
            "wall_sec": profile.get("wall_sec"),
        },
        "observable_source_features": {
            "input_mode": mode,
            "precision_tokens": sorted(set(re.findall(r"(?:float32|float64|np\.single|np\.double)", source, flags=re.IGNORECASE))),
            "uses_explicit_output_buffer": bool(re.search(r"\bout\s*=", source)),
            "uses_explicit_buffer_reset": bool(re.search(r"\.fill\(", source)),
            "uses_symmetry_related_terms": bool(symmetry_evidence),
            "uses_named_block_batch_chunk_or_tile": bool(blocking_evidence),
            "loop_structure": ast_counts(source),
        },
        "evidence_lines": {
            "input_loading": load_evidence,
            "precision": precision_evidence,
            "buffer_reuse": buffer_evidence,
            "symmetry": symmetry_evidence,
            "blocking_or_tiling": blocking_evidence[:8],
            "matrix_operations": matmul_evidence,
        },
        "interpretation_boundary": (
            "Feature presence is source-observable. It does not establish that a feature alone caused the observed RSS."
        ),
    }


def relative_pair_id(trial_id: str) -> str:
    return re.sub(r"_[AD]$", "", trial_id)


def markdown(records: list[dict[str, Any]]) -> str:
    direct = [record for record in records if record["cohort"] == "fresh_128mb_direct_api"]
    sweep = [record for record in records if record["cohort"] == "fresh_96mb_local_sweep"]
    by_trial = {record["trial_id"]: record for record in direct}
    lines = [
        "# Fresh Generated-Code Transformation Audit",
        "",
        "**Status:** Generated from archived scripts and metadata by `benchmarks/build_fresh_code_audit.py`.",
        "",
        "This is a complete, source-linked feature audit of the 30 included fresh 128 MB direct-API scripts and 15 retained executable 96 MB local-sweep scripts. It records only observable source features; it does not infer model intent or claim that any individual feature alone caused a measured MaxRSS change.",
        "",
        "The machine-readable companion is `experiments/06_replication/audit/fresh_code_transformation_audit.json`. Every row points to an archived source path and its SHA-256 digest. The raw scripts remain the authoritative record; the complete evidence package must be committed and release-tagged before public submission.",
        "",
        "## Classification rules",
        "",
        "- **Input mode:** `numpy_mmap` only when source explicitly supplies `mmap_mode=` to `np.load`; `numpy_load` when it calls `np.load` without that token.",
        "- **Named blocking:** true only when source contains a named block/batch/chunk/tile parameter or an associated `range` expression. It does not say that the program is optimally bounded.",
        "- **Output reuse/reset:** syntactic detection of `out=` or `.fill()` respectively.",
        "- **Symmetry-related terms:** syntactic detection of `triu`, `tril`, upper/lower-triangle text, or a `* 2` expression; it is not a correctness proof.",
        "- **AST parseability:** Python AST parsing under the audit interpreter. This is not a runtime compatibility test. The known Claude `opus_rep04_A` Python-3.9 runtime compatibility failure remains a recorded first-pass failure.",
        "",
        "## 128 MB direct-API paired cohort",
        "",
        "| Model | Pair | Blind features | Disclosed features | Observed RSS (MB), blind -> disclosed | Notes |",
        "|---|---|---|---|---:|---|",
    ]
    for model, ids in DIRECT_IDS.items():
        for index in range(0, len(ids), 2):
            blind = by_trial[ids[index]]
            disclosed = by_trial[ids[index + 1]]
            def concise(record: dict[str, Any]) -> str:
                f = record["observable_source_features"]
                parts = [f["input_mode"], "named-block" if f["uses_named_block_batch_chunk_or_tile"] else "no-named-block"]
                if f["uses_explicit_output_buffer"]:
                    parts.append("out-buffer")
                if f["uses_explicit_buffer_reset"]:
                    parts.append("buffer-reset")
                if f["precision_tokens"]:
                    parts.append("/".join(f["precision_tokens"]))
                return ", ".join(parts)
            blind_rss = blind["execution"]["maxrss_mb"]
            disclosed_rss = disclosed["execution"]["maxrss_mb"]
            rss = f"{blind_rss:.2f} -> {disclosed_rss:.2f}" if blind_rss is not None and disclosed_rss is not None else "not jointly executable"
            note = "" if blind["execution"]["correct"] else "Blind source failed on the pinned Python 3.9 runtime; its measured RSS is not used in executable-pair means."
            lines.append(f"| {model} | `{relative_pair_id(blind['trial_id'])}` | {concise(blind)} | {concise(disclosed)} | {rss} | {note} |")
    lines.extend([
        "",
        "## 96 MB condition-level extension",
        "",
        "These are independently sampled condition-level 96 MB-aware scripts, not matched triples with the 128 MB pairs. All were locally profiled for observed RSS; no OS cgroup admission or kill was used for this table.",
        "",
        "| Model | Retained trial | Source features | Observed RSS (MB) | Correct |",
        "|---|---|---|---:|---|",
    ])
    for record in sweep:
        f = record["observable_source_features"]
        parts = [f["input_mode"], "named-block" if f["uses_named_block_batch_chunk_or_tile"] else "no-named-block"]
        if f["uses_explicit_output_buffer"]:
            parts.append("out-buffer")
        if f["precision_tokens"]:
            parts.append("/".join(f["precision_tokens"]))
        lines.append(f"| {record['model_configured_id']} | `{record['trial_id']}` | {', '.join(parts)} | {record['execution']['maxrss_mb']:.2f} | {'yes' if record['execution']['correct'] else 'no'} |")
    lines.extend([
        "",
        "## Reproduction",
        "",
        "```bash",
        ".venv/bin/python3 benchmarks/build_fresh_code_audit.py --overwrite",
        "```",
        "",
        "The command fails if a retained source or metadata file is missing. It does not call a model API or modify any raw artifact.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true", help="replace generated audit files")
    args = parser.parse_args()
    if not args.overwrite and (AUDIT_JSON.exists() or AUDIT_MARKDOWN.exists()):
        raise SystemExit("Audit output exists; rerun with --overwrite to replace it.")

    records: list[dict[str, Any]] = []
    for model, trial_ids in DIRECT_IDS.items():
        for trial_id in trial_ids:
            directory = DIRECT_ROOT / model / trial_id
            if not (directory / "script.py").exists() or not (directory / "metadata.json").exists():
                raise FileNotFoundError(f"Missing retained direct artifact: {directory}")
            records.append(audit_program(model, trial_id, "fresh_128mb_direct_api", directory))
    for model, trial_ids in SWEEP_IDS.items():
        for trial_id in trial_ids:
            directory = SWEEP_ROOT / model / trial_id
            required = (directory / "script.py", directory / "generation_metadata.json", directory / "local_observed_rss_profile.json")
            if not all(path.exists() for path in required):
                raise FileNotFoundError(f"Missing retained 96 MB artifact: {directory}")
            records.append(audit_program(model, trial_id, "fresh_96mb_local_sweep", directory))

    payload = {
        "schema_version": "fresh-code-transformation-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "fresh_128mb_direct_api_scripts": 30,
            "fresh_96mb_local_sweep_retained_executable_scripts": 15,
            "excluded_from_128mb_analysis": ["opus_rep01_A", "opus_rep01_D"],
            "not_retained_as_96mb_executable_programs": ["opus96_rep03_D", "opus96_rep05_D"],
        },
        "classification_rules_version": "v1-source-observable-only",
        "records": records,
    }
    AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_MARKDOWN.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_MARKDOWN.write_text(markdown(records), encoding="utf-8")
    print(f"Wrote {len(records)} source-linked records to {AUDIT_JSON.relative_to(ROOT)}")
    print(f"Wrote human-readable report to {AUDIT_MARKDOWN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
