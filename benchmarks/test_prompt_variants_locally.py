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
# CONFIGURATION
# =====================================================================
MODEL_NAME = os.environ.get("SCAC_MODEL", "gemini-2.5-flash")
GCP_PROJECT = os.environ.get("GCP_PROJECT", "project-a9fc9225-58b8-41d1-bac")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")


def get_vertex_token() -> str:
    token = os.environ.get("VERTEX_TOKEN")
    if token:
        return token
    try:
        gcloud_bin = shutil.which("gcloud") or "/Users/manuagrawal/Downloads/google-cloud-sdk/bin/gcloud"
        env = dict(os.environ)
        if "CLOUDSDK_PYTHON" not in env:
            env["CLOUDSDK_PYTHON"] = sys.executable
        out = subprocess.check_output([gcloud_bin, "auth", "print-access-token"], text=True, env=env)
        return out.strip()
    except Exception as e:
        print(f"[!] Warning: Token fetch failed ({e})")
        return ""


def query_llm(prompt: str) -> str:
    token = get_vertex_token()
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if token:
        url = f"https://{GCP_LOCATION}-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT}/locations/{GCP_LOCATION}/publishers/google/models/{MODEL_NAME}:generateContent"
        req_data = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1}
        }
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            data=json.dumps(req_data).encode("utf-8")
        )
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={gemini_key}"
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
    sandbox = tempfile.mkdtemp(prefix="profile_run_")
    script_path = os.path.join(sandbox, "run.py")

    src = os.path.abspath(os.path.join(data_dir, "vectors.npy"))
    dst = os.path.join(sandbox, "vectors.npy")
    try:
        os.symlink(src, dst)
    except OSError:
        shutil.copy2(src, dst)

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code_str)

    # Use tracemalloc / time inside process wrapper
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


def test_all_variants():
    os.makedirs("./foil_data", exist_ok=True)
    npy_file = "./foil_data/vectors.npy"
    if not os.path.exists(npy_file):
        mat = np.random.randn(8000, 1024).astype(np.float32)
        np.save(npy_file, mat)

    base_prompt = (
        "Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).\n"
        "Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.\n"
        "Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."
    )

    variants = {
        "Variant A (Blind - No Substrate Context)": base_prompt,
        "Variant B (Aware - 128 MB RAM Ceiling)": f"{base_prompt}\n\nExecution environment:\nRAM limit: 128 MB.",
        "Variant C (Aware - 2,048 MB RAM Ceiling)": f"{base_prompt}\n\nExecution environment:\nRAM limit: 2048 MB.",
        "Variant D (Aware - 128 MB RAM + 10s Time Quota)": f"{base_prompt}\n\nExecution environment:\nRAM limit: 128 MB.\nExecution time limit: 10.0 seconds.\nOptimization Strategy: Use vectorized block/chunk processing (e.g. block size 1000)."
    }

    results = {}

    print("===================================================================================")
    print(f"   RAPID PROMPT VARIANT AUDIT (Model: {MODEL_NAME})")
    print("===================================================================================\n")

    for name, prompt in variants.items():
        print(f"[*] Testing {name}...")
        try:
            code = query_llm(prompt)
            profile = run_code_and_profile(code)
            results[name] = {
                "code": code,
                "profile": profile
            }
            print(f"    -> Profile: Time={profile['wall_sec']}s | Peak RAM Addr={profile['peak_mb']} MB | Success={profile['success']}")
        except Exception as e:
            print(f"    [!] Error testing {name}: {e}")

    # Output detailed summary table and code snippets
    print("\n" + "=" * 95)
    print(f"{'Variant':<45} | {'Peak RAM':<12} | {'Time (s)':<10} | {'Status':<10}")
    print("-" * 95)
    for name, data in results.items():
        prof = data["profile"]
        status_str = "✅ PASS" if prof["success"] else "❌ FAIL/TIMEOUT"
        print(f"{name:<45} | {prof['peak_mb']:<8.2f} MB | {prof['wall_sec']:<10.2f} | {status_str:<10}")
    print("=" * 95)

    with open("prompt_variant_comparison.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n[+] Exported detailed prompt variant code and metrics to prompt_variant_comparison.json.")

if __name__ == "__main__":
    test_all_variants()
