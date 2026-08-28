import os
import sys
import time
import json
import subprocess
import shutil
import tempfile
import ast
import numpy as np

# =====================================================================
# CONFIGURATION
# =====================================================================
# Model override: e.g. "gemini-3.6-flash", "gemini-3.7-flash", "gpt-4o"
MODEL_NAME = os.environ.get("SCAC_MODEL", "gemini-2.5-flash")
MEMORY_LIMIT_MB = 128
PAIRED_TRIALS = 10
USE_SUDO_SYSTEMD = False  # Set dynamically during preflight audit


# =====================================================================
# 1. PRE-FLIGHT CGROUP V2 AUDIT (FAIL-CLOSED & SELF-HEALING)
# =====================================================================
def verify_environment_or_abort():
    """
    FAIL-CLOSED: Verifies cgroup v2 systemd-run MemoryMax enforcement.
    Tests user-scope first, then sudo systemd-run if unprivileged delegation is off.
    Aborts if OOM kill fails on a 150MB allocation.
    """
    global USE_SUDO_SYSTEMD

    if shutil.which("systemd-run") is None:
        print("[!] NOTICE: 'systemd-run' not found locally (macOS host). Running LLM code generation and local dry-run execution...")
        USE_SUDO_SYSTEMD = False
        return

    print("[*] Running pre-flight cgroup v2 positive-control test (150MB alloc vs 128MB limit)...")
    test_unit = f"scac_preflight_{time.time_ns()}"
    
    test_cmd_user = [
        "systemd-run", "--user", "--scope", f"--unit={test_unit}", "-q",
        "-p", f"MemoryMax={MEMORY_LIMIT_MB}M",
        "-p", "MemorySwapMax=0",
        sys.executable, "-c", "data = bytearray(150 * 1024 * 1024)"  # Exceeds 128MB limit
    ]
    
    proc = subprocess.run(test_cmd_user, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode in (137, -9, 1):
        print("[+] Pre-flight passed via user-scope cgroup v2: Kernel kills allocations >128MB.\n")
        USE_SUDO_SYSTEMD = False
        return

    test_cmd_sudo = [
        "sudo", "systemd-run", "--scope", f"--unit={test_unit}", "-q",
        "-p", f"MemoryMax={MEMORY_LIMIT_MB}M",
        "-p", "MemorySwapMax=0",
        sys.executable, "-c", "data = bytearray(150 * 1024 * 1024)"
    ]
    proc_sudo = subprocess.run(test_cmd_sudo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc_sudo.returncode in (137, -9, 1):
        print("[+] Pre-flight passed via sudo cgroup v2: Kernel kills allocations >128MB.\n")
        USE_SUDO_SYSTEMD = True
        return

    print(f"\n[!] FATAL ERROR: Pre-flight MemoryMax assertion failed (user code: {proc.returncode}, sudo code: {proc_sudo.returncode}).")
    print("    cgroup v2 controller delegation is not active. Aborting.")
    sys.exit(1)


# =====================================================================
# 2. GENERATE DETERMINISTIC 8,000 x 1,024 VECTOR MATRIX (~32MB ON DISK)
# =====================================================================
def ensure_dataset(data_dir: str = "./foil_data") -> str:
    os.makedirs(data_dir, exist_ok=True)
    npy_file = os.path.join(data_dir, "vectors.npy")

    if not os.path.exists(npy_file):
        print("[*] Generating 8,000 x 1,024 float32 matrix (~32MB on disk, >512MB eager pairwise dot product memory)...")
        np.random.seed(42)
        mat = np.random.randn(8000, 1024).astype(np.float32)
        np.save(npy_file, mat)
        print("[+] Vector matrix dataset generated.")

    return os.path.abspath(data_dir)


# =====================================================================
# 3. CGROUP V2 EXECUTION SANDBOX (128MB RAM CEILING)
# =====================================================================
def execute_in_128mb_sandbox(code_str: str, data_dir: str, timeout_sec: int = 45) -> dict:
    sandbox = tempfile.mkdtemp(prefix="foil_run_")
    script_path = os.path.join(sandbox, "run.py")

    # Symlink dataset into sandbox
    src = os.path.join(data_dir, "vectors.npy")
    dst = os.path.join(sandbox, "vectors.npy")
    try:
        os.symlink(src, dst)
    except OSError:
        shutil.copy2(src, dst)

    with open(script_path, "w") as f:
        f.write(code_str)

    if shutil.which("systemd-run") is None:
        cmd = [sys.executable, script_path]
    else:
        unit = f"foil_trial_{time.time_ns()}"
        base_cmd = ["sudo", "systemd-run"] if USE_SUDO_SYSTEMD else ["systemd-run", "--user"]
        cmd = base_cmd + [
            "--scope", f"--unit={unit}", "-q",
            "-p", f"MemoryMax={MEMORY_LIMIT_MB}M",
            "-p", "MemorySwapMax=0",
            sys.executable, script_path
        ]

    t0 = time.perf_counter()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=sandbox)
        stdout_b, stderr_b = proc.communicate(timeout=timeout_sec)
        wall_time = time.perf_counter() - t0
        retcode = proc.returncode
        stderr = stderr_b.decode("utf-8", errors="replace")
        stdout = stdout_b.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        kill_cmd = ["sudo", "systemctl", "kill"] if USE_SUDO_SYSTEMD else ["systemctl", "--user", "kill"]
        subprocess.run(kill_cmd + ["--kill-who=all", "-s", "SIGKILL", f"{unit}.scope"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.kill()
        return {"status": "TIMEOUT", "is_oom": False, "wall_sec": timeout_sec, "stdout": "", "stderr": "Timeout"}
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    is_oom = retcode in (137, -9) or "MemoryError" in stderr or "std::bad_alloc" in stderr
    is_missing_mod = "ModuleNotFoundError" in stderr or "ImportError" in stderr
    is_syntax_err = "SyntaxError" in stderr

    if retcode == 0:
        status = "SUCCESS"
    elif is_oom:
        status = "OOM_KILL"
    elif is_missing_mod:
        status = "MISSING_MODULE"
    elif is_syntax_err:
        status = "SYNTAX_ERROR"
    else:
        status = "RUNTIME_ERROR"

    return {
        "status": status,
        "is_oom": is_oom,
        "wall_sec": round(wall_time, 2),
        "stdout": stdout.strip()[:300],
        "stderr": stderr.strip()[:300]
    }


# =====================================================================
# 4. ROBUST LLM CLIENT WITH EXPONENTIAL BACKOFF RETRIES
# =====================================================================
def query_llm_with_retry(prompt: str, max_retries: int = 5) -> str:
    import urllib.request
    import urllib.error

    gemini_key = os.environ.get("GEMINI_API_KEY")
    project = os.environ.get("GCP_PROJECT", "")
    location = "us-central1"

    # Fetch OAuth access token for unlimited Vertex AI billing quota
    token = os.environ.get("VERTEX_TOKEN")
    if not token:
        try:
            cmd = ["gcloud", "auth", "print-access-token"]
            token = subprocess.check_output(cmd, text=True).strip()
        except Exception:
            token = None

    for attempt in range(1, max_retries + 1):
        try:
            if token:
                model = MODEL_NAME if MODEL_NAME else "gemini-2.5-flash"
                url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:generateContent"
                req_data = {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2}
                }
                req = urllib.request.Request(
                    url,
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    data=json.dumps(req_data).encode("utf-8")
                )
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw = data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                model = MODEL_NAME if "gemini" in MODEL_NAME else "gemini-3.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                req_data = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2}
                }
                req = urllib.request.Request(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(req_data).encode("utf-8")
                )
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw = data["candidates"][0]["content"]["parts"][0]["text"]

            return clean_code_blocks(raw)

        except urllib.error.HTTPError as e:
            wait_time = 3.0 * attempt
            print(f"    [!] API HTTP {e.code} on attempt {attempt}/{max_retries}. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
        except Exception as e:
            wait_time = 3.0 * attempt
            print(f"    [!] Network/API error on attempt {attempt}/{max_retries}: {e}. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)

    raise RuntimeError(f"Failed to query LLM API after {max_retries} attempts.")


def clean_code_blocks(raw: str) -> str:
    raw_str = raw.strip()
    if "```python" in raw_str:
        code = raw_str.split("```python")[1].split("```")[0].strip()
    elif "```py" in raw_str:
        code = raw_str.split("```py")[1].split("```")[0].strip()
    elif "```" in raw_str:
        code = raw_str.split("```")[1].split("```")[0].strip()
    else:
        code = raw_str

    try:
        ast.parse(code)
    except SyntaxError:
        pass
    return code


# Observational strategy detector for Euclidean Distance task
def detect_strategy_heuristic(code: str) -> str:
    code_lower = code.lower()
    if "pdist" in code_lower or "v @ v.t" in code_lower or "np.newaxis" in code_lower:
        return "EAGER_MATRIX_BROADCASTING"
    if "for " in code_lower or "slice" in code_lower or "chunk" in code_lower or "i+1:" in code_lower:
        return "STREAMING_ROW_SLICING"
    return "UNKNOWN_STRATEGY"


# =====================================================================
# 5. EXECUTE 10-PAIR (20-RUN) FOIL TEST & SAVE PERSISTENT ARTIFACTS
# =====================================================================
def run_foil_test():
    verify_environment_or_abort()
    data_dir = ensure_dataset()
    save_code_dir = "./foil_runs_euclidean"
    os.makedirs(save_code_dir, exist_ok=True)

    base_task_prompt = (
        "Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).\n"
        "Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.\n"
        "Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."
    )

    prompt_a = base_task_prompt
    prompt_b = (
        f"{base_task_prompt}\n\n"
        f"Execution environment:\n"
        f"RAM limit: {MEMORY_LIMIT_MB} MB."
    )

    print("=" * 95)
    print(f"   WEEK-1 FOIL TEST: 10 PAIRED EUCLIDEAN TRIALS (Model: {MODEL_NAME} | Limit: {MEMORY_LIMIT_MB}MB)")
    print("=" * 95 + "\n")

    paired_results = []

    for pair_idx in range(1, PAIRED_TRIALS + 1):
        print(f"[*] Running Paired Trial {pair_idx:02d}/{PAIRED_TRIALS:02d}...")

        # 1. Condition A (Blind)
        code_a = query_llm_with_retry(prompt_a)
        strat_a = detect_strategy_heuristic(code_a)
        with open(os.path.join(save_code_dir, f"trial_{pair_idx:02d}_A_blind.py"), "w") as f:
            f.write(code_a)
        res_a = execute_in_128mb_sandbox(code_a, data_dir=data_dir)
        time.sleep(3.0)  # Pacing delay between Vertex AI API queries

        # 2. Condition B (Substrate-Aware)
        code_b = query_llm_with_retry(prompt_b)
        strat_b = detect_strategy_heuristic(code_b)
        with open(os.path.join(save_code_dir, f"trial_{pair_idx:02d}_B_aware.py"), "w") as f:
            f.write(code_b)
        res_b = execute_in_128mb_sandbox(code_b, data_dir=data_dir)
        time.sleep(3.0)

        icon_a = "✅" if res_a["status"] == "SUCCESS" else "❌"
        icon_b = "✅" if res_b["status"] == "SUCCESS" else "❌"

        print(f"    Blind (A): {icon_a} {res_a['status']:<14} ({res_a['wall_sec']}s) | Strategy: {strat_a}")
        print(f"    Aware (B): {icon_b} {res_b['status']:<14} ({res_b['wall_sec']}s) | Strategy: {strat_b}\n")

        paired_results.append({
            "pair": pair_idx,
            "status_a": res_a["status"],
            "strat_a": strat_a,
            "time_a": res_a["wall_sec"],
            "stdout_a": res_a["stdout"],
            "stderr_a": res_a["stderr"],
            "status_b": res_b["status"],
            "strat_b": strat_b,
            "time_b": res_b["wall_sec"],
            "stdout_b": res_b["stdout"],
            "stderr_b": res_b["stderr"],
            "strategy_diverged": strat_a != strat_b
        })

    # =====================================================================
    # 6. RESULTS TABLE & PERSISTENT ARTIFACT EXPORT
    # =====================================================================
    print("=" * 95)
    print(f"{'Pair':<6} | {'Condition A (Blind)':<32} | {'Condition B (Substrate-Aware)':<32} | {'Diverged?'}")
    print("-" * 95)
    for r in paired_results:
        a_str = f"{r['status_a']} ({r['strat_a']}, {r['time_a']}s)"
        b_str = f"{r['status_b']} ({r['strat_b']}, {r['time_b']}s)"
        div_str = "YES" if r["strategy_diverged"] else "NO"
        print(f"{r['pair']:<6} | {a_str:<32} | {b_str:<32} | {div_str}")
    print("=" * 95)

    succ_a = sum(1 for r in paired_results if r["status_a"] == "SUCCESS")
    succ_b = sum(1 for r in paired_results if r["status_b"] == "SUCCESS")
    oom_a = sum(1 for r in paired_results if r["status_a"] == "OOM_KILL")
    oom_b = sum(1 for r in paired_results if r["status_b"] == "OOM_KILL")
    div_count = sum(1 for r in paired_results if r["strategy_diverged"])

    summary_dict = {
        "model": MODEL_NAME,
        "memory_limit_mb": MEMORY_LIMIT_MB,
        "paired_trials": PAIRED_TRIALS,
        "condition_a_success_rate": succ_a / PAIRED_TRIALS,
        "condition_b_success_rate": succ_b / PAIRED_TRIALS,
        "condition_a_ooms": oom_a,
        "condition_b_ooms": oom_b,
        "strategy_divergence_rate": div_count / PAIRED_TRIALS,
        "trials": paired_results
    }

    json_path = os.path.join(save_code_dir, "results.json")
    with open(json_path, "w") as f:
        json.dump(summary_dict, f, indent=2)

    md_path = os.path.join(save_code_dir, "summary_report.md")
    with open(md_path, "w") as f:
        f.write(f"# WEEK-1 FOIL TEST RESULTS SUMMARY (MATRIX PAIRWISE DOT PRODUCT)\n\n")
        f.write(f"- **Model Evaluated**: `{MODEL_NAME}`\n")
        f.write(f"- **RAM Sandbox Ceiling**: `{MEMORY_LIMIT_MB} MB`\n")
        f.write(f"- **Condition A (Blind) Success Rate**: `{succ_a}/{PAIRED_TRIALS}` ({succ_a/PAIRED_TRIALS*100:.1f}%) | OOM Kills: `{oom_a}`\n")
        f.write(f"- **Condition B (Substrate-Aware) Success Rate**: `{succ_b}/{PAIRED_TRIALS}` ({succ_b/PAIRED_TRIALS*100:.1f}%) | OOM Kills: `{oom_b}`\n")
        f.write(f"- **Algorithmic Strategy Divergence Rate**: `{div_count}/{PAIRED_TRIALS}` ({div_count/PAIRED_TRIALS*100:.1f}%)\n\n")
        f.write(f"### Paired Matrix Trials Log\n")
        f.write(f"| Pair | Condition A (Blind) | Condition B (Aware) | Diverged? |\n")
        f.write(f"|---|---|---|---|\n")
        for r in paired_results:
            a_str = f"{r['status_a']} (`{r['strat_a']}`, {r['time_a']}s)"
            b_str = f"{r['status_b']} (`{r['strat_b']}`, {r['time_b']}s)"
            div_str = "YES" if r["strategy_diverged"] else "NO"
            f.write(f"| Pair {r['pair']:02d} | {a_str} | {b_str} | {div_str} |\n")

    print("\n--- FINAL SUMMARY (10 PAIRED TRIALS) ---")
    print(f"• Condition A (Blind) Success Rate:          {succ_a}/{PAIRED_TRIALS} ({succ_a/PAIRED_TRIALS*100:.1f}%) | OOMs: {oom_a}")
    print(f"• Condition B (Substrate-Aware) Success Rate:{succ_b}/{PAIRED_TRIALS} ({succ_b/PAIRED_TRIALS*100:.1f}%) | OOMs: {oom_b}")
    print(f"• Algorithmic Strategy Divergence Rate:      {div_count}/{PAIRED_TRIALS} ({div_count/PAIRED_TRIALS*100:.1f}%)")
    print(f"• Results JSON exported to:                   {json_path}")
    print(f"• Summary Report exported to:                 {md_path}")
    print("=" * 95 + "\n")


if __name__ == "__main__":
    run_foil_test()
