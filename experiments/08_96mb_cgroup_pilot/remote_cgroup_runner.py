#!/usr/bin/env python3
"""Run one script in a strict systemd cgroup and emit one JSON profile."""

import argparse
import json
import math
import os
import re
import subprocess
import time

GROUND_TRUTH = 2895556144.199324
MEMORY_MB = 96
WALL_SEC = 10


def read_file(path):
    result = subprocess.run(["sudo", "cat", path], text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def run_in_cgroup(command, label):
    unit = f"scac96_{label}_{time.time_ns()}"
    cmd = [
        "sudo", "systemd-run", "--unit", unit, "--wait", "--quiet", "--pipe",
        "-p", f"MemoryMax={MEMORY_MB}M", "-p", "MemorySwapMax=0",
        "-p", f"RuntimeMaxSec={WALL_SEC}", "-p", f"WorkingDirectory={os.getcwd()}",
        "--setenv=OMP_NUM_THREADS=1", "--setenv=OPENBLAS_NUM_THREADS=1",
        "--setenv=MKL_NUM_THREADS=1", "--setenv=VECLIB_MAXIMUM_THREADS=1",
        "--setenv=NUMEXPR_NUM_THREADS=1",
    ] + command
    start = time.perf_counter()
    proc = subprocess.run(cmd, text=True, capture_output=True)
    wall_sec = time.perf_counter() - start
    cgroup = f"/sys/fs/cgroup/system.slice/{unit}.service"
    events = read_file(f"{cgroup}/memory.events")
    peak = read_file(f"{cgroup}/memory.peak")
    show = subprocess.run(
        ["sudo", "systemctl", "show", unit, "--property=Result", "--property=ExecMainCode", "--property=ExecMainStatus"],
        text=True, capture_output=True
    ).stdout.strip()
    subprocess.run(["sudo", "systemctl", "reset-failed", unit], capture_output=True)
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
            "wall_sec": wall_sec, "memory_events": events, "memory_peak_bytes": peak,
            "systemd_status": show, "unit": unit}


def event_count(events, key):
    match = re.search(rf"^{re.escape(key)}\s+(\d+)$", events or "", re.MULTILINE)
    return int(match.group(1)) if match else 0


def was_oom_killed(raw):
    """Use cgroup events when retained; systemd's result is the fallback after cleanup."""
    return (event_count(raw["memory_events"], "oom_kill") >= 1 or
            "Result=oom-kill" in raw["systemd_status"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    if args.preflight:
        raw = run_in_cgroup(["python3", "-c", "x=bytearray(150*1024*1024)"], args.label)
        raw["positive_control_passed"] = was_oom_killed(raw)
    else:
        if not args.script:
            raise SystemExit("--script is required unless --preflight is used")
        raw = run_in_cgroup(["python3", args.script], args.label)
        match = re.search(r"TOTAL_DIST:\s*([0-9eE.+-]+)", raw["stdout"])
        total = float(match.group(1)) if match else None
        correct = total is not None and math.isfinite(total) and abs(total - GROUND_TRUTH) / GROUND_TRUTH < 1e-4
        oom = was_oom_killed(raw)
        raw.update({"total_dist": total, "correct": correct, "oom_kill": oom,
                    "success": raw["returncode"] == 0 and correct})
    print(json.dumps(raw, indent=2))


if __name__ == "__main__":
    main()
