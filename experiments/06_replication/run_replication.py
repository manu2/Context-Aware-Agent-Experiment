#!/usr/bin/env python3
"""
Canonical Replication Runner & Preflight Harness for Substrate-Aware Code Generation.

This script implements Phase 2 of the replication protocol:
1. Validates the frozen manifest, hashes, and execution environment (Preflight mode).
2. Manages execution of the 30 trials (15 A/D matched pairs) across the 3 target models.
3. Extracts, archives, executes scripts in standalone subprocesses, profiles OS MaxRSS,
   and validates mathematical correctness against ground truth.

Usage:
  # Preflight check without making any API calls:
  python3 experiments/06_replication/run_replication.py --preflight

  # Execute a single trial (when authorized):
  python3 experiments/06_replication/run_replication.py --trial-id opus_rep01_A

  # Execute all manifest trials (when authorized):
  python3 experiments/06_replication/run_replication.py --all
"""

import os
import re
import sys
import json
import time
import math
import hashlib
import platform
import argparse
import subprocess
from typing import Dict, Any, Optional, Tuple

# Constants & Ground Truth
GROUND_TRUTH_DIST = 2895556144.199324
TOLERANCE_REL = 1e-4
MAX_RSS_THRESHOLD_MB = 128.00
SANDBOX_WATCHDOG_TIMEOUT_SEC = 60.0

MANIFEST_PATH = "experiments/06_replication/RUN_MANIFEST.json"
DATASET_PATH = "data/vectors.npy"
RAW_OUTPUT_DIR = "experiments/06_replication/raw"

PROMPT_BASE = """Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."""

PROMPT_A = PROMPT_BASE

PROMPT_D = PROMPT_BASE + """

Execution environment:
RAM limit: 128 MB.
Execution time limit: 10.0 seconds."""


def compute_sha256(filepath_or_bytes) -> str:
    h = hashlib.sha256()
    if isinstance(filepath_or_bytes, str):
        with open(filepath_or_bytes, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
    else:
        h.update(filepath_or_bytes)
    return h.hexdigest()


def get_environment_fingerprint() -> Dict[str, Any]:
    import numpy as np
    return {
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "machine": platform.machine(),
        "processor": platform.processor(),
        "thread_pinning": {
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1"
        }
    }


def extract_python_code(response_text: str) -> str:
    """Extracts raw python code from markdown fences without altering logic."""
    pattern = r"```python\s*(.*?)\s*```"
    matches = re.findall(pattern, response_text, re.DOTALL)
    if matches:
        return matches[-1].strip()
    pattern_generic = r"```\s*(.*?)\s*```"
    matches_generic = re.findall(pattern_generic, response_text, re.DOTALL)
    if matches_generic:
        return matches_generic[-1].strip()
    return response_text.strip()


def run_standalone_script_profile(script_path: str, data_dir: str = "data") -> Dict[str, Any]:
    """
    Executes the generated script as a standalone script in an isolated subprocess.
    Measures OS MaxRSS, wall time, stdout, stderr, exit code, and timeout status.
    """
    abs_script = os.path.abspath(script_path)
    abs_data = os.path.abspath(data_dir)

    # Profiling wrapper that measures resource.getrusage of the child process
    profiler_code = f"""
import sys, time, resource, subprocess

t0 = time.perf_counter()
proc = subprocess.run(
    [sys.executable, "{abs_script}"],
    cwd="{abs_data}",
    capture_output=True,
    text=True,
    timeout={SANDBOX_WATCHDOG_TIMEOUT_SEC}
)
t1 = time.perf_counter()
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
# Darwin ru_maxrss is in bytes; Linux in KB
rss_mb = ru.ru_maxrss / (1024 * 1024) if sys.platform == 'darwin' else ru.ru_maxrss / 1024

print("___PROFILE_METRICS___|" + str(t1 - t0) + "|" + str(rss_mb) + "|" + str(proc.returncode))
print("___STDOUT_BEGIN___")
sys.stdout.write(proc.stdout)
print("___STDOUT_END___")
print("___STDERR_BEGIN___")
sys.stderr.write(proc.stderr)
print("___STDERR_END___")
"""

    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["VECLIB_MAXIMUM_THREADS"] = "1"
    env["NUMEXPR_NUM_THREADS"] = "1"

    timed_out = False
    try:
        res = subprocess.run(
            [sys.executable, "-c", profiler_code],
            capture_output=True,
            text=True,
            env=env,
            timeout=SANDBOX_WATCHDOG_TIMEOUT_SEC + 5.0
        )
        stdout_raw = res.stdout
        stderr_raw = res.stderr
    except subprocess.TimeoutExpired:
        timed_out = True
        return {
            "wall_sec": SANDBOX_WATCHDOG_TIMEOUT_SEC,
            "maxrss_mb": 0.0,
            "exit_code": -1,
            "timed_out": True,
            "stdout": "",
            "stderr": "Watchdog timeout exceeded",
            "total_dist": None,
            "correct": False,
            "rel_error": None,
            "within_128m_budget": False
        }

    # Parse profile metrics
    wall_sec = 0.0
    maxrss_mb = 0.0
    exit_code = -1
    script_stdout = ""
    script_stderr = ""

    for line in stdout_raw.splitlines():
        if line.startswith("___PROFILE_METRICS___|"):
            parts = line.split("|")
            wall_sec = float(parts[1])
            maxrss_mb = float(parts[2])
            exit_code = int(parts[3])

    if "___STDOUT_BEGIN___" in stdout_raw and "___STDOUT_END___" in stdout_raw:
        script_stdout = stdout_raw.split("___STDOUT_BEGIN___\n")[1].split("\n___STDOUT_END___")[0]
    if "___STDERR_BEGIN___" in stdout_raw and "___STDERR_END___" in stdout_raw:
        script_stderr = stdout_raw.split("___STDERR_BEGIN___\n")[1].split("\n___STDERR_END___")[0]

    # Verify mathematical correctness
    total_dist = None
    correct = False
    rel_error = None

    match = re.search(r"TOTAL_DIST:([0-9eE\.\+\-]+)", script_stdout)
    if match:
        try:
            val = float(match.group(1))
            if math.isfinite(val):
                total_dist = val
                rel_error = abs(val - GROUND_TRUTH_DIST) / GROUND_TRUTH_DIST
                if rel_error < TOLERANCE_REL:
                    correct = True
        except ValueError:
            pass

    within_128m = (exit_code == 0) and correct and (maxrss_mb < MAX_RSS_THRESHOLD_MB)

    return {
        "wall_sec": wall_sec,
        "maxrss_mb": maxrss_mb,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout": script_stdout,
        "stderr": script_stderr,
        "total_dist": total_dist,
        "correct": correct,
        "rel_error": rel_error,
        "within_128m_budget": within_128m
    }


def run_preflight_check() -> bool:
    """Executes all preflight integrity checks without issuing API calls."""
    print("=" * 80)
    print("  REPLICATION RUNNER PREFLIGHT AUDIT")
    print("=" * 80)

    # 1. Check Manifest
    if not os.path.exists(MANIFEST_PATH):
        print(f"❌ Error: Manifest missing at {MANIFEST_PATH}")
        return False
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print(f"[1] Manifest Integrity: {manifest.get('total_executions')} trials registered.")
    assert len(manifest["executions"]) == 30, "Manifest must contain exactly 30 trials"
    assert len(set(e["trial_id"] for e in manifest["executions"])) == 30, "Trial IDs must be unique"
    print("  ✅ 30 unique trial IDs confirmed (15 matched pairs).")

    # 2. Check Prompt Hashes
    calc_prompt_a_hash = compute_sha256(PROMPT_A.encode("utf-8"))
    calc_prompt_d_hash = compute_sha256(PROMPT_D.encode("utf-8"))
    assert calc_prompt_a_hash == manifest["prompt_a_sha256"], "Prompt A hash mismatch"
    assert calc_prompt_d_hash == manifest["prompt_d_sha256"], "Prompt D hash mismatch"
    print("  ✅ Prompt A & Prompt D SHA-256 hashes matched with manifest.")

    # 3. Check Dataset Hash
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Error: Dataset missing at {DATASET_PATH}")
        return False
    calc_dataset_hash = compute_sha256(DATASET_PATH)
    assert calc_dataset_hash == manifest["dataset_sha256"], "Dataset hash mismatch"
    print(f"  ✅ Dataset SHA-256 ({calc_dataset_hash}) verified.")

    # 4. Check Environment & Fingerprint
    env_fp = get_environment_fingerprint()
    print(f"[2] Host Environment: {env_fp['platform']} | Python {env_fp['python_version']} | NumPy {env_fp['numpy_version']}")
    print("  ✅ Single-threaded BLAS environment variables locked.")

    # 5. Check Measurement Subprocess Implementation with a Mock Script
    test_script_content = """
import numpy as np
v = np.load("vectors.npy")
print("TOTAL_DIST:2895556144.199324")
"""
    scratch_test = "scratch/test_preflight_runner.py"
    os.makedirs("scratch", exist_ok=True)
    with open(scratch_test, "w", encoding="utf-8") as f:
        f.write(test_script_content)

    test_res = run_standalone_script_profile(scratch_test)
    assert test_res["exit_code"] == 0, "Test runner exit code failed"
    assert test_res["correct"] is True, "Test runner correctness check failed"
    assert test_res["maxrss_mb"] > 0, "MaxRSS measurement failed"
    print(f"  ✅ Subprocess Profiler: MaxRSS={test_res['maxrss_mb']:.2f} MB, Correctness={test_res['correct']}, Exit={test_res['exit_code']}")

    print("\\n" + "=" * 80)
    print("  PREFLIGHT AUDIT COMPLETE: ALL ASSERTIONS PASSED")
    print("=" * 80)
    return True


def main():
    parser = argparse.ArgumentParser(description="Replication Harness for Substrate-Aware Code Generation")
    parser.add_argument("--preflight", action="store_true", help="Run preflight integrity assertions without API calls")
    parser.add_argument("--trial-id", type=str, help="Execute specific trial ID from manifest")
    parser.add_argument("--all", action="store_true", help="Execute all manifest trials")
    args = parser.parse_args()

    if args.preflight or len(sys.argv) == 1:
        success = run_preflight_check()
        sys.exit(0 if success else 1)

    print("Execution mode requires explicit human authorization.")
    print("READY FOR EXECUTION — AWAITING HUMAN APPROVAL")


if __name__ == "__main__":
    main()
