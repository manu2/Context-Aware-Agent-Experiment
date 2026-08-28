import os
import sys
import time
import json
import ast
import urllib.request
import urllib.error
import subprocess
import shutil
import tempfile
import numpy as np

# =====================================================================
# CONFIGURATION & MULTI-MODEL ROUTER
# =====================================================================
GCP_PROJECT = os.environ.get("GCP_PROJECT", "")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")


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
        return ""


def query_llm_router(prompt: str, model_id: str = "gemini-2.5-flash") -> str:
    """
    Unified multi-model caller supporting:
    - Gemini (Vertex AI / AI Studio)
    - Anthropic (Claude via ANTHROPIC_API_KEY)
    - OpenAI (GPT-4o via OPENAI_API_KEY)
    - DeepSeek (via DEEPSEEK_API_KEY)
    """
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    vertex_token = get_vertex_token()

    # --- ANTHROPIC CLAUDE ROUTE ---
    if "claude" in model_id.lower():
        if not anthropic_key:
            raise ValueError(f"ANTHROPIC_API_KEY not found in environment for model {model_id}.")
        url = "https://api.anthropic.com/v1/messages"
        req_data = {
            "model": model_id,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        req = urllib.request.Request(
            url,
            headers={
                "x-api-key": anthropic_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            data=json.dumps(req_data).encode("utf-8")
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["content"][0]["text"]
        return clean_code_blocks(raw)

    # --- OPENAI ROUTE ---
    elif "gpt" in model_id.lower() or "o3" in model_id.lower() or "o1" in model_id.lower():
        if not openai_key:
            raise ValueError(f"OPENAI_API_KEY not found in environment for model {model_id}.")
        url = "https://api.openai.com/v1/chat/completions"
        req_data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps(req_data).encode("utf-8")
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"]
        return clean_code_blocks(raw)

    # --- DEEPSEEK ROUTE ---
    elif "deepseek" in model_id.lower():
        if not deepseek_key:
            raise ValueError(f"DEEPSEEK_API_KEY not found in environment for model {model_id}.")
        url = "https://api.deepseek.com/chat/completions"
        req_data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {deepseek_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps(req_data).encode("utf-8")
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"]
        return clean_code_blocks(raw)

    # --- GOOGLE GEMINI ROUTE (DEFAULT) ---
    else:
        if vertex_token:
            url = f"https://{GCP_LOCATION}-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT}/locations/{GCP_LOCATION}/publishers/google/models/{model_id}:generateContent"
            req_data = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1}
            }
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {vertex_token}", "Content-Type": "application/json"},
                data=json.dumps(req_data).encode("utf-8")
            )
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={gemini_key}"
            req_data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1}
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
    return code


def run_code_and_profile(code_str: str, data_dir: str = "./foil_data") -> dict:
    sandbox = tempfile.mkdtemp(prefix="multi_model_run_")
    script_path = os.path.join(sandbox, "run.py")

    src = os.path.abspath(os.path.join(data_dir, "vectors.npy"))
    dst = os.path.join(sandbox, "vectors.npy")
    try:
        os.symlink(src, dst)
    except OSError:
        shutil.copy2(src, dst)

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code_str)

    wrapper_code = f"""
import sys, time, tracemalloc
tracemalloc.start()
t0 = time.perf_counter()
try:
    with open("{script_path}") as f:
        exec(f.read(), {{'__file__': '{script_path}', '__name__': '__main__'}})
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"\\n___PROFILE_RESULT___|{{t1 - t0:.4f}}|{{peak / 1024 / 1024:.2f}}|0")
except Exception as e:
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"\\n___PROFILE_RESULT___|{{t1 - t0:.4f}}|{{peak / 1024 / 1024:.2f}}|1|{{e}}")
"""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", wrapper_code],
            cwd=sandbox,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            text=True
        )
        stdout = proc.stdout
        stderr = proc.stderr
        wall_sec = 0.0
        peak_mb = 0.0
        err_flag = 0

        for line in stdout.splitlines():
            if "___PROFILE_RESULT___" in line:
                parts = line.split("|")
                wall_sec = float(parts[1])
                peak_mb = float(parts[2])
                err_flag = int(parts[3])

        return {
            "wall_sec": wall_sec,
            "peak_mb": peak_mb,
            "success": err_flag == 0 and "TOTAL_DIST:" in stdout,
            "stdout": stdout.strip()[:300],
            "stderr": stderr.strip()[:300]
        }
    except subprocess.TimeoutExpired:
        return {
            "wall_sec": 30.0,
            "peak_mb": 0.0,
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out (30.0s)"
        }
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def test_natural_language_vs_telemetry(model_id: str = "gemini-2.5-flash"):
    os.makedirs("./foil_data", exist_ok=True)
    npy_file = "./foil_data/vectors.npy"
    if not os.path.exists(npy_file):
        mat = np.random.randn(8000, 1024).astype(np.float32)
        np.save(npy_file, mat)

    base_task = (
        "Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).\n"
        "Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.\n"
        "Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."
    )

    conditions = {
        "1. Blind (No Hardware Context)": base_task,
        "2. Natural Language Advice (Vague: 'Write memory-efficient code')": f"{base_task}\n\nOptimization note: Please ensure your code is highly memory-efficient and avoids large memory allocations.",
        "3. Explicit 2D Telemetry (SCAC: 128MB RAM + 10s Time Quota)": f"{base_task}\n\nExecution environment:\nRAM limit: 128 MB.\nExecution time limit: 10.0 seconds.\nOptimization Strategy: Use vectorized block/chunk processing (e.g. block size 1000)."
    }

    print(f"===================================================================================")
    print(f"  CRITICAL BASELINE AUDIT: NATURAL LANGUAGE vs. EXPLICIT TELEMETRY ({model_id})")
    print(f"===================================================================================\n")

    results = {}
    for cond_name, prompt_text in conditions.items():
        print(f"[*] Testing: {cond_name}...")
        try:
            code = query_llm_router(prompt_text, model_id=model_id)
            profile = run_code_and_profile(code)
            results[cond_name] = {"code": code, "profile": profile}
            print(f"    -> Peak RAM: {profile['peak_mb']:.2f} MB | Time: {profile['wall_sec']:.2f}s | Success: {profile['success']}")
        except Exception as e:
            print(f"    [!] Error testing {cond_name}: {e}")

    print("\n" + "=" * 95)
    print(f"{'Condition':<50} | {'Peak RAM':<12} | {'Time (s)':<10} | {'Status':<10}")
    print("-" * 95)
    for name, data in results.items():
        prof = data["profile"]
        status_str = "✅ PASS" if prof["success"] else "❌ FAIL/OOM/TIMEOUT"
        print(f"{name:<50} | {prof['peak_mb']:<8.2f} MB | {prof['wall_sec']:<10.2f} | {status_str:<10}")
    print("=" * 95)

    with open("natural_language_vs_telemetry_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n[+] Results saved to natural_language_vs_telemetry_results.json.")

if __name__ == "__main__":
    target_model = os.environ.get("SCAC_MODEL", "gemini-2.5-flash")
    test_natural_language_vs_telemetry(model_id=target_model)
