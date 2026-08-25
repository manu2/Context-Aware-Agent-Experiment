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
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

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


def query_anthropic_model(prompt: str, model_id: str = "claude-sonnet-5") -> str:
    url = "https://api.anthropic.com/v1/messages"
    req_data = {
        "model": model_id,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    }
    req = urllib.request.Request(
        url,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        },
        data=json.dumps(req_data).encode("utf-8")
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        text_parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        raw = "".join(text_parts)
        return clean_code_blocks(raw)


def profile_code(code_str: str, data_dir: str = "./foil_data") -> dict:
    sandbox = tempfile.mkdtemp(prefix="scac_eval_")
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
            timeout=40,
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
            "wall_sec": 40.0,
            "peak_mb": 0.0,
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out (40.0s)"
        }
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def main():
    target_model = "claude-sonnet-5"
    out_dir = "./local_experiments/frontier_model_benchmark"
    os.makedirs(f"{out_dir}/runs", exist_ok=True)

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

    print(f"===================================================================================")
    print(f"  EXECUTING FULL SCAC 4-CONDITION SUITE FOR: {target_model.upper()}")
    print(f"===================================================================================\n")

    results = {}
    json_file = f"{out_dir}/{target_model}_results.json"

    for var_key, var_info in variants.items():
        print(f"[*] Querying {target_model} for: {var_key}...")
        prompt_text = var_info["prompt"]
        code = query_anthropic_model(prompt_text, model_id=target_model)
        
        safe_key = var_key.split(" ")[1].replace("(", "").replace(")", "").lower()
        script_file = f"{out_dir}/runs/{safe_key}_{target_model}.py"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(code)
            
        print(f"    Saved code -> {script_file}")
        print(f"    Profiling execution locally...")
        prof = profile_code(code)
        
        status_sym = "✅ PASS" if prof["success"] else "❌ FAIL/TIMEOUT"
        print(f"    -> {status_sym} | Peak RAM: {prof['peak_mb']:.2f} MB | Latency: {prof['wall_sec']:.4f}s")
        if not prof["success"] and prof["stderr"]:
            print(f"       Stderr: {prof['stderr']}")
            
        results[var_key] = {
            "model": target_model,
            "description": var_info["desc"],
            "script_path": script_file,
            "code": code,
            "profile": prof
        }
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        time.sleep(1.0)

    print("\n" + "=" * 95)
    print(f"{'Condition':<40} | {'Peak RAM':<12} | {'Time (s)':<10} | {'128MB Status':<15}")
    print("-" * 95)
    for k, v in results.items():
        p = v["profile"]
        if not p["success"]:
            stat = "❌ TIMEOUT/ERROR"
        elif p["peak_mb"] > 128.0:
            stat = f"💥 OOM ({p['peak_mb']:.1f}MB)"
        else:
            stat = "✅ PASS"
        print(f"{k:<40} | {p['peak_mb']:<8.2f} MB | {p['wall_sec']:<10.4f} | {stat:<15}")
    print("=" * 95)
    print(f"\n[+] Suite complete for {target_model}! Saved to {json_file}")

if __name__ == "__main__":
    main()
