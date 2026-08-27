#!/usr/bin/env python3
"""Profile an archived 96 MB-aware pilot script locally; no API calls occur here."""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "06_replication"))
from run_replication import get_environment_fingerprint, run_standalone_script_profile  # noqa: E402

MANIFEST_PATH = ROOT / "experiments" / "08_96mb_cgroup_pilot" / "RUN_MANIFEST.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-id", required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST_PATH.read_text())
    trial = next((x for x in manifest["executions"] if x["trial_id"] == args.trial_id), None)
    if trial is None:
        raise SystemExit(f"Unknown predeclared trial ID: {args.trial_id}")
    model_label = trial.get("model", "gpt-5.6-sol")
    trial_dir = ROOT / "experiments" / "08_96mb_cgroup_pilot" / "raw" / model_label / args.trial_id
    script = trial_dir / "script.py"
    out = trial_dir / "local_observed_rss_profile.json"
    if not script.is_file():
        raise SystemExit(f"Missing archived script: {script}")
    if out.exists():
        raise SystemExit(f"Refusing to overwrite local profile: {out}")
    profile = run_standalone_script_profile(str(script), data_dir="data")
    out.write_text(json.dumps({
        "trial_id": args.trial_id,
        "measurement": "macOS isolated-child RUSAGE_CHILDREN MaxRSS; observed classification, not cgroup enforcement",
        "environment": get_environment_fingerprint(),
        "profile": profile,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }, indent=2))
    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
