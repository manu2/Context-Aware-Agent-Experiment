#!/usr/bin/env python3
"""Generate one atomically archived GPT 96 MB pilot pair; do not execute it locally."""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "06_replication"))
from run_replication import extract_python_code, query_model  # noqa: E402

PILOT_DIR = ROOT / "experiments" / "08_96mb_cgroup_pilot"
MANIFEST_PATH = PILOT_DIR / "RUN_MANIFEST.json"
PROMPT_BASE = """Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."""
PROMPT_D_96 = PROMPT_BASE + """

Execution environment:
RAM limit: 96 MB.
Execution time limit: 10.0 seconds."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-id", required=True)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text())
    trial = next((x for x in manifest["executions"] if x["trial_id"] == args.trial_id), None)
    if trial is None:
        raise SystemExit(f"Unknown predeclared trial ID: {args.trial_id}")
    if sha256(ROOT / "data" / "vectors.npy") != manifest["dataset_sha256"]:
        raise SystemExit("Dataset SHA-256 mismatch; refusing generation")

    model_label = trial.get("model", "gpt-5.6-sol")
    model_config = manifest.get("models", {}).get(model_label, manifest["model"])
    prompt = PROMPT_BASE if trial["condition"] == "A_Blind" else PROMPT_D_96
    trial_dir = PILOT_DIR / "raw" / model_label / trial["trial_id"]
    trial_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        trial_dir.mkdir()
    except FileExistsError as exc:
        raise SystemExit(f"Refusing to overwrite existing pilot artifact: {trial_dir}") from exc

    try:
        response = query_model(model_config, prompt)
    except Exception as exc:
        (trial_dir / "failure_metadata.json").write_text(json.dumps({
            "trial_id": trial["trial_id"], "pair_id": trial["pair_id"],
            "condition": trial["condition"], "status": "generation_failed", "error": str(exc),
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }, indent=2))
        raise

    code = extract_python_code(response)
    (trial_dir / "raw_response.txt").write_text(response)
    (trial_dir / "script.py").write_text(code)
    (trial_dir / "generation_metadata.json").write_text(json.dumps({
        "trial_id": trial["trial_id"], "pair_id": trial["pair_id"],
        "condition": trial["condition"], "model": model_config,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "dataset_sha256": manifest["dataset_sha256"],
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }, indent=2))
    print(f"Archived generation: {trial_dir}")


if __name__ == "__main__":
    main()
