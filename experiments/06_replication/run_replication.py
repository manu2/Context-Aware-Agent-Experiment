#!/usr/bin/env python3
"""
Canonical Replication Runner & Preflight Harness for Substrate-Aware Code Generation.

Implements the end-to-end execution pipeline for the 30-trial replication study:
1. Preflight validation of manifest, dataset hash, prompt hashes, and environment assertions.
2. Live querying of Anthropic, OpenAI, and Google Gemini API endpoints.
3. Extraction and archiving of raw responses, exact generated scripts, and metadata.json.
4. Standalone subprocess execution profiling with correct timeout handling, stderr capturing,
   OS-level MaxRSS tracking, mathematical correctness assertion (<1e-4 relative error),
   and 128 MB budget compliance classification.

Usage:
  # Preflight check without making any API calls:
  python3 experiments/06_replication/run_replication.py --preflight

  # Execute a specific trial:
  python3 experiments/06_replication/run_replication.py --trial-id opus_rep01_A

  # Execute all 30 manifest trials:
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
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple

# Constants & Ground Truth
GROUND_TRUTH_DIST = 2895556144.199324
TOLERANCE_REL = 1e-4
MAX_RSS_THRESHOLD_MB = 128.00
PROMPT_DECLARED_TIME_SEC = 10.0
SANDBOX_WATCHDOG_TIMEOUT_SEC = 60.0

MANIFEST_PATH = "experiments/06_replication/RUN_MANIFEST.json"
DATASET_PATH = "data/vectors.npy"
RAW_OUTPUT_DIR = "experiments/06_replication/raw"

# Auto-load .env file if present in workspace root
def load_env_file(env_path: str = ".env"):
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v

load_env_file(".env")


FROZEN_PYTHON_VERSION = "3.9.6"
FROZEN_NUMPY_VERSION = "2.0.2"
FROZEN_PLATFORM_PREFIX = "macOS"

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
    Measures OS MaxRSS, wall time, stdout, stderr, exit code, timeout, and correctness.
    """
    abs_script = os.path.abspath(script_path)
    abs_data = os.path.abspath(data_dir)

    # Profiling wrapper that executes the standalone script with watchdog timeout
    profiler_code = f"""
import sys, time, resource, subprocess, json

t0 = time.perf_counter()
timed_out = False
exit_code = -1
stdout_txt = ""
stderr_txt = ""

try:
    proc = subprocess.run(
        [sys.executable, "{abs_script}"],
        cwd="{abs_data}",
        capture_output=True,
        text=True,
        timeout={SANDBOX_WATCHDOG_TIMEOUT_SEC}
    )
    t1 = time.perf_counter()
    exit_code = proc.returncode
    stdout_txt = proc.stdout
    stderr_txt = proc.stderr
except subprocess.TimeoutExpired as te:
    t1 = time.perf_counter()
    timed_out = True
    exit_code = -9
    stdout_txt = te.stdout or ""
    stderr_txt = (te.stderr or "") + "\\\\n[WATCHDOG_TIMEOUT: 60.0s exceeded]"

ru = resource.getrusage(resource.RUSAGE_CHILDREN)
# Darwin ru_maxrss is in bytes; Linux in KB
rss_mb = ru.ru_maxrss / (1024 * 1024) if sys.platform == 'darwin' else ru.ru_maxrss / 1024

profile_dict = {{
    "wall_sec": t1 - t0,
    "maxrss_mb": rss_mb,
    "exit_code": exit_code,
    "timed_out": timed_out,
    "stdout": stdout_txt,
    "stderr": stderr_txt
}}

print("___PROFILE_JSON_START___")
print(json.dumps(profile_dict))
print("___PROFILE_JSON_END___")
"""

    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    env["VECLIB_MAXIMUM_THREADS"] = "1"
    env["NUMEXPR_NUM_THREADS"] = "1"

    try:
        res = subprocess.run(
            [sys.executable, "-c", profiler_code],
            capture_output=True,
            text=True,
            env=env,
            timeout=SANDBOX_WATCHDOG_TIMEOUT_SEC + 5.0
        )
        wrapper_stdout = res.stdout
    except subprocess.TimeoutExpired:
        return {
            "wall_sec": SANDBOX_WATCHDOG_TIMEOUT_SEC,
            "maxrss_mb": 0.0,
            "exit_code": -9,
            "timed_out": True,
            "stdout": "",
            "stderr": "Watchdog outer runner timeout expired",
            "total_dist": None,
            "correct": False,
            "rel_error": None,
            "within_128m_budget": False,
            "within_10s_budget": False
        }

    # Parse JSON profile
    prof_data = {}
    if "___PROFILE_JSON_START___" in wrapper_stdout and "___PROFILE_JSON_END___" in wrapper_stdout:
        json_str = wrapper_stdout.split("___PROFILE_JSON_START___\n")[1].split("\n___PROFILE_JSON_END___")[0]
        try:
            prof_data = json.loads(json_str)
        except Exception:
            pass

    wall_sec = prof_data.get("wall_sec", 0.0)
    maxrss_mb = prof_data.get("maxrss_mb", 0.0)
    exit_code = prof_data.get("exit_code", -1)
    timed_out = prof_data.get("timed_out", False)
    script_stdout = prof_data.get("stdout", "")
    script_stderr = prof_data.get("stderr", "")

    # Verify mathematical correctness
    total_dist = None
    correct = False
    rel_error = None

    match = re.search(r"TOTAL_DIST:\s*([0-9eE\.\+\-]+)", script_stdout)
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
    within_10s = (exit_code == 0) and correct and (wall_sec <= PROMPT_DECLARED_TIME_SEC)

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
        "within_128m_budget": within_128m,
        "within_10s_budget": within_10s
    }


def query_model(model_config: Dict[str, Any], prompt: str, max_retries: int = 3) -> str:
    """Executes live API call to the specified model provider endpoint with retries."""
    provider = model_config["provider"]
    api_model_id = model_config["api_model_id"]
    endpoint = model_config["endpoint"]
    temperature = model_config["temperature"]

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            if provider == "anthropic":
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    raise RuntimeError("Missing ANTHROPIC_API_KEY environment variable")
                req_data = {
                    "model": api_model_id,
                    "max_tokens": model_config.get("max_tokens", 4096),
                    "temperature": temperature,
                    "top_p": model_config.get("top_p", 1.0),
                    "messages": [{"role": "user", "content": prompt}]
                }
                req = urllib.request.Request(
                    endpoint,
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    data=json.dumps(req_data).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data.get("content", [])
                    return "".join([b.get("text", "") for b in content if b.get("type") == "text"])

            elif provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise RuntimeError("Missing OPENAI_API_KEY environment variable")
                req_data = {
                    "model": api_model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "top_p": model_config.get("top_p", 1.0)
                }
                if "max_completion_tokens" in model_config:
                    req_data["max_completion_tokens"] = model_config["max_completion_tokens"]
                req = urllib.request.Request(
                    endpoint,
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    data=json.dumps(req_data).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"]

            elif provider == "google":
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key:
                    raise RuntimeError("Missing GEMINI_API_KEY for Google AI Studio API")

                req_data = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": model_config.get("max_output_tokens", 8192),
                        "topP": model_config.get("top_p", 0.95)
                    }
                }
                req = urllib.request.Request(
                    endpoint,
                    headers={
                        "x-goog-api-key": api_key,
                        "Content-Type": "application/json"
                    },
                    data=json.dumps(req_data).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise RuntimeError(f"Gemini returned empty candidates: {data}")
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if not parts:
                        finish_reason = candidates[0].get("finishReason", "UNKNOWN")
                        raise RuntimeError(f"Gemini response has no text parts (finishReason: {finish_reason})")
                    return parts[0].get("text", "")

            else:
                raise ValueError(f"Unknown provider: {provider}")

        except Exception as e:
            # Mask any accidental key leakage in exception messages
            err_msg = str(e)
            for k in [os.environ.get("OPENAI_API_KEY"), os.environ.get("ANTHROPIC_API_KEY"), os.environ.get("GEMINI_API_KEY")]:
                if k and k in err_msg:
                    err_msg = err_msg.replace(k, "[REDACTED_API_KEY]")
            last_error = err_msg
            print(f"    [!] API attempt {attempt}/{max_retries} failed ({err_msg}). Retrying in {attempt * 3}s...")
            time.sleep(attempt * 3)

    raise RuntimeError(f"Model query failed after {max_retries} attempts: {last_error}")


def execute_trial(execution_meta: Dict[str, Any], model_config: Dict[str, Any]) -> Dict[str, Any]:
    trial_id = execution_meta["trial_id"]
    model_name = execution_meta["model"]
    condition = execution_meta["condition"]
    pair_id = execution_meta["pair_id"]

    prompt = PROMPT_A if "A_Blind" in condition else PROMPT_D
    prompt_name = "Condition A (Blind)" if "A_Blind" in condition else "Condition D (2D Telemetry)"

    print(f"\n[*] Executing {trial_id} | Model: {model_config['api_model_id']} | {prompt_name}...")

    # 1. Query model
    t_gen_0 = time.perf_counter()
    raw_response = query_model(model_config, prompt)
    t_gen_1 = time.perf_counter()
    gen_time_sec = t_gen_1 - t_gen_0

    # 2. Extract code
    code = extract_python_code(raw_response)

    # 3. Create run directory
    trial_dir = os.path.join(RAW_OUTPUT_DIR, model_name, trial_id)
    os.makedirs(trial_dir, exist_ok=True)

    raw_response_path = os.path.join(trial_dir, "raw_response.txt")
    script_path = os.path.join(trial_dir, "script.py")
    metadata_path = os.path.join(trial_dir, "metadata.json")

    with open(raw_response_path, "w", encoding="utf-8") as f:
        f.write(raw_response)

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    # 4. Profile standalone script
    profile_res = run_standalone_script_profile(script_path, data_dir="data")

    # 5. Save metadata.json
    metadata = {
        "trial_id": trial_id,
        "model_label": model_name,
        "pair_id": pair_id,
        "condition": condition,
        "model_config": model_config,
        "generation_time_sec": gen_time_sec,
        "environment": get_environment_fingerprint(),
        "profile": profile_res,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    status_icon = "✅" if profile_res["within_128m_budget"] else "💥"
    print(f"    {status_icon} MaxRSS: {profile_res['maxrss_mb']:.2f} MB | Time: {profile_res['wall_sec']:.4f}s | Correct: {profile_res['correct']} | Exit: {profile_res['exit_code']}")
    return metadata


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

    # 3. Check Dataset Hash & Generator
    if not os.path.exists(DATASET_PATH):
        print(f"[*] Dataset missing. Running deterministic generator data/generate_dataset.py...")
        from data.generate_dataset import generate_dataset
        generate_dataset(DATASET_PATH)

    calc_dataset_hash = compute_sha256(DATASET_PATH)
    assert calc_dataset_hash == manifest["dataset_sha256"], "Dataset hash mismatch"
    print(f"  ✅ Dataset SHA-256 ({calc_dataset_hash}) verified.")

    # 4. Check Environment & Fingerprint Assertions
    env_fp = get_environment_fingerprint()
    print(f"[2] Host Environment: {env_fp['platform']} | Python {env_fp['python_version']} | NumPy {env_fp['numpy_version']}")
    assert env_fp["python_version"] == FROZEN_PYTHON_VERSION, f"Python version mismatch: expected {FROZEN_PYTHON_VERSION}, got {env_fp['python_version']}"
    assert env_fp["numpy_version"] == FROZEN_NUMPY_VERSION, f"NumPy version mismatch: expected {FROZEN_NUMPY_VERSION}, got {env_fp['numpy_version']}"
    assert env_fp["platform"].startswith(FROZEN_PLATFORM_PREFIX), f"Platform mismatch: expected {FROZEN_PLATFORM_PREFIX}, got {env_fp['platform']}"
    print("  ✅ Python 3.9.6, NumPy 2.0.2, and macOS platform strictly asserted.")

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

    # 6. Check Failure Paths (Exit code, Stderr, and Timeout)
    test_err_script = """
import sys
sys.stderr.write("TEST_STDERR_MESSAGE\\n")
sys.exit(1)
"""
    scratch_err_test = "scratch/test_err_runner.py"
    with open(scratch_err_test, "w", encoding="utf-8") as f:
        f.write(test_err_script)

    err_res = run_standalone_script_profile(scratch_err_test)
    assert err_res["exit_code"] == 1, "Exit code 1 not captured"
    assert "TEST_STDERR_MESSAGE" in err_res["stderr"], "Stderr not captured"
    print(f"  ✅ Error & Stderr Handling Verified (Exit={err_res['exit_code']}, Stderr captured).")

    test_timeout_script = """
import time
time.sleep(2.0)
"""
    scratch_timeout_test = "scratch/test_timeout_runner.py"
    with open(scratch_timeout_test, "w", encoding="utf-8") as f:
        f.write(test_timeout_script)

    # Test short watchdog timeout
    global SANDBOX_WATCHDOG_TIMEOUT_SEC
    orig_timeout = SANDBOX_WATCHDOG_TIMEOUT_SEC
    SANDBOX_WATCHDOG_TIMEOUT_SEC = 0.5
    try:
        timeout_res = run_standalone_script_profile(scratch_timeout_test)
        assert timeout_res["timed_out"] is True, "Timeout status not recorded"
        assert timeout_res["exit_code"] == -9, "Timeout exit code not -9"
        assert "WATCHDOG_TIMEOUT" in timeout_res["stderr"], "Watchdog stderr message missing"
        print(f"  ✅ Timeout Failure Path Verified (timed_out=True, exit=-9, notice captured).")
    finally:
        SANDBOX_WATCHDOG_TIMEOUT_SEC = orig_timeout

    print("\n" + "=" * 80)
    print("  PREFLIGHT AUDIT COMPLETE: ALL ASSERTIONS PASSED")
    print("=" * 80)
    return True


def main():
    parser = argparse.ArgumentParser(description="Replication Harness for Substrate-Aware Code Generation")
    parser.add_argument("--preflight", action="store_true", help="Run preflight integrity assertions without API calls")
    parser.add_argument("--trial-id", type=str, help="Execute specific trial ID from manifest")
    parser.add_argument("--all", action="store_true", help="Execute all manifest trials")
    args = parser.parse_args()

    # Preflight MUST execute and pass before any live run or inspection
    if not run_preflight_check():
        print("❌ Preflight check failed. Aborting all operations.")
        sys.exit(1)

    if args.preflight or len(sys.argv) == 1:
        print("\n[+] System is fully verified.")
        print("READY FOR EXECUTION — AWAITING HUMAN APPROVAL")
        sys.exit(0)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    models_config = manifest["models"]
    executions = manifest["executions"]

    if args.trial_id:
        target_exec = next((e for e in executions if e["trial_id"] == args.trial_id), None)
        if not target_exec:
            print(f"❌ Error: Trial ID {args.trial_id} not found in manifest.")
            sys.exit(1)
        model_cfg = models_config[target_exec["model"]]
        execute_trial(target_exec, model_cfg)

    elif args.all:
        print(f"[*] Beginning execution of {len(executions)} replication trials...")
        all_results = []
        summary_file = "experiments/06_replication/replication_summary.json"
        
        for idx, e in enumerate(executions, 1):
            model_cfg = models_config[e["model"]]
            print(f"\n--- Running Trial [{idx}/{len(executions)}]: {e['trial_id']} ---")
            res = execute_trial(e, model_cfg)
            all_results.append(res)
            
            # Save progress incrementally after every trial
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump({"executions": all_results}, f, indent=2)
            
            time.sleep(2)  # Respect rate limits

        print(f"\n[+] Replication complete. Full summary written to {summary_file}")


if __name__ == "__main__":
    main()
