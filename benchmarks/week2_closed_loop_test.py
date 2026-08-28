import os
import sys
import time
import json
import subprocess
import shutil
import tempfile
import ast
import urllib.request
import urllib.error
import numpy as np

# =====================================================================
# CONFIGURATION
# =====================================================================
MODEL_NAME = os.environ.get("SCAC_MODEL", "gemini-2.5-flash")
MEMORY_LIMIT_MB = int(os.environ.get("SCAC_MEMORY_LIMIT", "128"))
GCP_PROJECT = os.environ.get("GCP_PROJECT", "")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")


# =====================================================================
# 1. DATASET GENERATOR (8,000 x 1,024 float32 matrix ~32.8MB on disk)
# =====================================================================
def ensure_dataset(data_dir: str = "./foil_data") -> str:
    os.makedirs(data_dir, exist_ok=True)
    npy_file = os.path.join(data_dir, "vectors.npy")

    if not os.path.exists(npy_file):
        print("[*] Generating 8,000 x 1,024 float32 matrix (~32.8MB on disk)...")
        np.random.seed(42)
        mat = np.random.randn(8000, 1024).astype(np.float32)
        np.save(npy_file, mat)
        print("[+] Vector matrix dataset generated.")

    return os.path.abspath(data_dir)


# =====================================================================
# 2. LOCAL & CGROUP V2 SANDBOX EXECUTOR
# =====================================================================
def execute_in_sandbox(code_str: str, data_dir: str, memory_limit_mb: int = 128, timeout_sec: int = 45) -> dict:
    sandbox = tempfile.mkdtemp(prefix="scac_closed_loop_")
    script_path = os.path.join(sandbox, "run.py")

    # Symlink dataset into sandbox
    src = os.path.join(data_dir, "vectors.npy")
    dst = os.path.join(sandbox, "vectors.npy")
    try:
        os.symlink(src, dst)
    except OSError:
        shutil.copy2(src, dst)

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code_str)

    has_systemd = shutil.which("systemd-run") is not None
    unit_name = f"scac_trial_{time.time_ns()}"

    if has_systemd:
        cmd = [
            "systemd-run", "--user", "--scope", f"--unit={unit_name}", "-q",
            "-p", f"MemoryMax={memory_limit_mb}M",
            "-p", "MemorySwapMax=0",
            sys.executable, script_path
        ]
    else:
        # Local macOS execution fallback
        cmd = [sys.executable, script_path]

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=sandbox,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_sec,
            text=True
        )
        wall_time = time.perf_counter() - t0
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as e:
        wall_time = timeout_sec
        returncode = 124  # SIGALRM / Timeout
        stdout = e.stdout.decode("utf-8") if e.stdout else ""
        stderr = "Execution timed out after 45.0 seconds."
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    is_oom = returncode in (137, -9) or "MemoryError" in stderr or "Killed" in stderr
    is_success = returncode == 0 and "TOTAL_DIST:" in stdout

    return {
        "returncode": returncode,
        "is_success": is_success,
        "is_oom": is_oom,
        "wall_sec": round(wall_time, 2),
        "stdout": stdout.strip()[:400],
        "stderr": stderr.strip()[:400]
    }


# =====================================================================
# 3. VERTEX AI / LLM CLIENT WITH OAUTH TOKEN RESOLUTION
# =====================================================================
def get_vertex_token() -> str:
    token = os.environ.get("VERTEX_TOKEN")
    if token:
        return token
    try:
        gcloud_bin = shutil.which("gcloud")
        if not gcloud_bin:
            return ""
        env = dict(os.environ)
        if "CLOUDSDK_PYTHON" not in env:
            env["CLOUDSDK_PYTHON"] = sys.executable
        out = subprocess.check_output([gcloud_bin, "auth", "print-access-token"], text=True, env=env)
        return out.strip()
    except Exception as e:
        print(f"[!] Warning: Failed to fetch gcloud token ({e}). Falling back to GEMINI_API_KEY...")
        return ""


def query_llm(messages: list, max_retries: int = 5) -> str:
    token = get_vertex_token()
    gemini_key = os.environ.get("GEMINI_API_KEY")

    for attempt in range(1, max_retries + 1):
        try:
            if token:
                url = f"https://{GCP_LOCATION}-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT}/locations/{GCP_LOCATION}/publishers/google/models/{MODEL_NAME}:generateContent"
                contents = []
                for msg in messages:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": msg["content"]}]})

                req_data = {
                    "contents": contents,
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
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={gemini_key}"
                contents = [{"parts": [{"text": msg["content"]}]} for msg in messages]
                req_data = {
                    "contents": contents,
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
            wait_time = 2.0 * attempt
            print(f"    [!] API HTTP {e.code} on attempt {attempt}/{max_retries}. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
        except Exception as e:
            wait_time = 2.0 * attempt
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


# =====================================================================
# 4. SINGLE-TRIAL 2-TURN CLOSED-LOOP EXECUTOR
# =====================================================================
def run_single_closed_loop_trial(is_substrate_aware: bool = True, memory_limit_mb: int = 128):
    data_dir = ensure_dataset()

    base_task_prompt = (
        "Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).\n"
        "Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.\n"
        "Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."
    )

    if is_substrate_aware:
        prompt_turn1 = f"{base_task_prompt}\n\nExecution environment:\nRAM limit: {memory_limit_mb} MB."
    else:
        prompt_turn1 = base_task_prompt

    messages = [{"role": "user", "content": prompt_turn1}]

    print(f"\n[*] --- RUNNING CLOSED-LOOP TRIAL (Model: {MODEL_NAME} | Aware: {is_substrate_aware} | RAM Ceiling: {memory_limit_mb} MB) ---")
    
    # === TURN 1 ===
    print("    [Turn 1] Querying LLM for Turn 1 code generation...")
    t0_gen = time.perf_counter()
    code_turn1 = query_llm(messages)
    gen_time_turn1 = round(time.perf_counter() - t0_gen, 2)
    print(f"    [Turn 1] Code generated in {gen_time_turn1}s. Executing in sandbox...")

    res_turn1 = execute_in_sandbox(code_turn1, data_dir, memory_limit_mb=memory_limit_mb)
    print(f"    [Turn 1 Result] Status: {'✅ SUCCESS' if res_turn1['is_success'] else '❌ FAILED (OOM/Err)'} | Exit Code: {res_turn1['returncode']} | Time: {res_turn1['wall_sec']}s")

    if res_turn1["is_success"]:
        print("    [+] Turn 1 achieved SUCCESS PASS on first attempt! No Turn 2 required.")
        return {
            "turn1": res_turn1,
            "turn2": None,
            "final_success": True,
            "turns_taken": 1
        }

    # === TURN 2 (Closed-Loop Telemetry Injection) ===
    telemetry_feedback = (
        f"[EXECUTION TELEMETRY FEEDBACK - TURN 1]\n"
        f"- Last Action Result: ❌ FAILED (Exit Code {res_turn1['returncode']})\n"
        f"- Wall-Clock Latency: {res_turn1['wall_sec']}s\n"
        f"- Substrate Ceiling: {memory_limit_mb} MB RAM\n"
        f"- Terminal Error Log:\n{res_turn1['stderr'] or res_turn1['stdout'] or 'Process exceeded resource limit'}\n\n"
        f"Instructions: Refactor your Python implementation to run successfully within the {memory_limit_mb} MB RAM limit and print 'TOTAL_DIST:<value>'."
    )

    messages.append({"role": "assistant", "content": code_turn1})
    messages.append({"role": "user", "content": telemetry_feedback})

    print("\n    [Turn 2] Injecting Telemetry Feedback Block into Turn 2 context...")
    t0_gen2 = time.perf_counter()
    code_turn2 = query_llm(messages)
    gen_time_turn2 = round(time.perf_counter() - t0_gen2, 2)
    print(f"    [Turn 2] Refactored code generated in {gen_time_turn2}s. Executing in sandbox...")

    res_turn2 = execute_in_sandbox(code_turn2, data_dir, memory_limit_mb=memory_limit_mb)
    print(f"    [Turn 2 Result] Status: {'✅ SUCCESS' if res_turn2['is_success'] else '❌ FAILED'} | Exit Code: {res_turn2['returncode']} | Time: {res_turn2['wall_sec']}s")

    return {
        "turn1": res_turn1,
        "turn2": res_turn2,
        "final_success": res_turn2["is_success"],
        "turns_taken": 2
    }


if __name__ == "__main__":
    print("===================================================================================")
    print(f"  SCAC PHASE 2: 2-TURN CLOSED-LOOP TELEMETRY EXPERIMENT (LOCAL TEST RUN)")
    print("===================================================================================")
    result = run_single_closed_loop_trial(is_substrate_aware=True, memory_limit_mb=128)
    print("\n[+] TRIAL SUMMARY RESULTS:")
    print(json.dumps(result, indent=2))
