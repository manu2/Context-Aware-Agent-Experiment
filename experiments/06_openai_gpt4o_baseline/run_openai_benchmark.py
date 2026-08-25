import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
import shutil
import tempfile
import numpy as np

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

def test_api_connection(model_id: str = "gpt-4o") -> bool:
    print(f"[*] Testing OpenAI API connectivity with model '{model_id}'...")
    url = "https://api.openai.com/v1/chat/completions"
    req_data = {
        "model": model_id,
        "messages": [{"role": "user", "content": "Respond with single word: OK"}],
        "max_tokens": 5,
        "temperature": 0.0
    }
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps(req_data).encode("utf-8")
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"].strip()
            print(f"[+] API connection verified! Response: {content}")
            return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"[!] HTTP Error {e.code}: {err_body}")
        return False
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        return False


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


def query_openai(prompt: str, model_id: str = "gpt-4o") -> str:
    url = "https://api.openai.com/v1/chat/completions"
    req_data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps(req_data).encode("utf-8")
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        raw = data["choices"][0]["message"]["content"]
    return clean_code_blocks(raw)


def profile_code(code_str: str, data_dir: str = "./foil_data") -> dict:
    sandbox = tempfile.mkdtemp(prefix="openai_run_")
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
            timeout=35,
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
            "stdout": stdout.strip()[:400],
            "stderr": stderr.strip()[:400]
        }
    except subprocess.TimeoutExpired:
        return {
            "wall_sec": 35.0,
            "peak_mb": 0.0,
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out (35.0s)"
        }
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def main():
    os.makedirs("./foil_data", exist_ok=True)
    os.makedirs("./local_experiments/openai_benchmark/runs", exist_ok=True)
    npy_file = "./foil_data/vectors.npy"
    if not os.path.exists(npy_file):
        print("[*] Generating synthetic vectors.npy (8000 x 1024 float32, ~32.8MB)...")
        np.random.seed(42)
        mat = np.random.randn(8000, 1024).astype(np.float32)
        np.save(npy_file, mat)

    target_model = "gpt-4o"
    if not test_api_connection(target_model):
        print("[!] Aborting benchmark due to API connection failure.")
        sys.exit(1)

    base_task = (
        "Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).\n"
        "Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.\n"
        "Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."
    )

    variants = {
        "Variant A (Blind)": {
            "prompt": base_task,
            "desc": "No hardware or memory context provided."
        },
        "Variant B (Natural Language Advice)": {
            "prompt": f"{base_task}\n\nOptimization note: Please ensure your code is highly memory-efficient and avoids large memory allocations.",
            "desc": "Unstructured natural language advice to be memory efficient."
        },
        "Variant C (1D Telemetry: 128MB RAM)": {
            "prompt": f"{base_task}\n\nExecution environment:\nRAM limit: 128 MB.",
            "desc": "Explicit 1D spatial telemetry (RAM limit: 128 MB)."
        },
        "Variant D (2D Telemetry: 128MB RAM + 10s CPU)": {
            "prompt": f"{base_task}\n\nExecution environment:\nRAM limit: 128 MB.\nExecution time limit: 10.0 seconds.",
            "desc": "Explicit 2D spatial + temporal telemetry (RAM limit: 128 MB, CPU quota: 10s)."
        }
    }

    print(f"\n===================================================================================")
    print(f"  SCAC MULTI-MODEL BENCHMARK: OPENAI {target_model.upper()} (4 PROMPT CONDITIONS)")
    print(f"===================================================================================\n")

    results = {}
    for var_key, var_info in variants.items():
        print(f"[*] Querying {target_model} for: {var_key}...")
        prompt_text = var_info["prompt"]
        code = query_openai(prompt_text, model_id=target_model)
        
        # Save script
        safe_name = var_key.split(" ")[1].replace("(", "").replace(")", "").lower()
        script_file = f"./local_experiments/openai_benchmark/runs/{safe_name}_{target_model}.py"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(code)
            
        print(f"    Saved code to {script_file}")
        print(f"    Profiling execution locally...")
        prof = profile_code(code)
        
        status_sym = "✅ PASS" if prof["success"] else "❌ FAIL/TIMEOUT"
        print(f"    -> Status: {status_sym} | Peak RAM: {prof['peak_mb']:.2f} MB | Time: {prof['wall_sec']:.2f}s")
        if not prof["success"] and prof["stderr"]:
            print(f"       Stderr: {prof['stderr']}")
            
        results[var_key] = {
            "description": var_info["desc"],
            "script_path": script_file,
            "code": code,
            "profile": prof
        }
        time.sleep(1.0) # Graceful delay

    out_json = "./local_experiments/openai_benchmark/openai_gpt4o_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 95)
    print(f"{'Prompt Condition':<40} | {'Peak RAM':<12} | {'Time (s)':<10} | {'Status':<12}")
    print("-" * 95)
    for k, v in results.items():
        p = v["profile"]
        stat = "✅ PASS" if p["success"] else "❌ FAIL"
        print(f"{k:<40} | {p['peak_mb']:<8.2f} MB | {p['wall_sec']:<10.2f} | {stat:<12}")
    print("=" * 95)
    print(f"\n[+] Full benchmark results saved to: {out_json}")

if __name__ == "__main__":
    main()
