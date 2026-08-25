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


def query_openai_model_with_retry(prompt: str, model_id: str = "gpt-5.6-sol", max_retries: int = 3) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    req_data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}]
    }
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                data=json.dumps(req_data).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=150) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw = data["choices"][0]["message"]["content"]
                return clean_code_blocks(raw)
        except Exception as e:
            print(f"    [!] OpenAI attempt {attempt}/{max_retries} failed ({e}), retrying in 5s...")
            time.sleep(5)
    raise RuntimeError(f"Failed to query OpenAI model {model_id} after {max_retries} attempts.")


def query_anthropic_model_with_retry(prompt: str, model_id: str = "claude-fable-5", max_retries: int = 3) -> str:
    url = "https://api.anthropic.com/v1/messages"
    req_data = {
        "model": model_id,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    }
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                data=json.dumps(req_data).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text_parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
                raw = "".join(text_parts)
                return clean_code_blocks(raw)
        except Exception as e:
            print(f"    [!] Anthropic attempt {attempt}/{max_retries} failed ({e}), retrying in 5s...")
            time.sleep(5)
    raise RuntimeError(f"Failed to query Anthropic model {model_id} after {max_retries} attempts.")


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


def run_full_suite_for_model(model_name: str, query_fn, output_dir: str):
    os.makedirs(f"{output_dir}/runs", exist_ok=True)
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
    print(f"  EXECUTING SCAC 4-CONDITION SUITE FOR MODEL: {model_name.upper()}")
    print(f"===================================================================================\n")

    results = {}
    json_file = f"{output_dir}/{model_name}_results.json"
    if os.path.exists(json_file):
        try:
            with open(json_file, "r") as f:
                results = json.load(f)
        except Exception:
            results = {}

    for var_key, var_info in variants.items():
        safe_key = var_key.split(" ")[1].replace("(", "").replace(")", "").lower()
        script_file = f"{output_dir}/runs/{safe_key}_{model_name}.py"

        # Check if already completed and valid
        if var_key in results and results[var_key]["profile"]["success"] and os.path.exists(script_file):
            print(f"[*] [{model_name}] {var_key} already completed -> RAM: {results[var_key]['profile']['peak_mb']:.2f} MB | Latency: {results[var_key]['profile']['wall_sec']:.4f}s")
            continue

        print(f"[*] [{model_name}] Querying condition: {var_key}...")
        prompt_text = var_info["prompt"]
        code = query_fn(prompt_text, model_id=model_name)
        
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
            "model": model_name,
            "description": var_info["desc"],
            "script_path": script_file,
            "code": code,
            "profile": prof
        }
        
        # Checkpoint incrementally
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
            
        time.sleep(2.0)

    print(f"\n[+] Suite complete for {model_name}. Results saved to {json_file}")
    return results


def main():
    os.makedirs("./foil_data", exist_ok=True)
    os.makedirs("./local_experiments/frontier_model_benchmark", exist_ok=True)
    npy_file = "./foil_data/vectors.npy"
    if not os.path.exists(npy_file):
        print("[*] Generating synthetic vectors.npy (8000 x 1024 float32, ~32.8MB)...")
        np.random.seed(42)
        mat = np.random.randn(8000, 1024).astype(np.float32)
        np.save(npy_file, mat)

    out_base = "./local_experiments/frontier_model_benchmark"

    # 1. Run full 4-condition suite on GPT-5.6-sol
    gpt_results = run_full_suite_for_model(
        model_name="gpt-5.6-sol",
        query_fn=query_openai_model_with_retry,
        output_dir=out_base
    )

    # 2. Run full 4-condition suite on Claude-Fable-5
    claude_results = run_full_suite_for_model(
        model_name="claude-fable-5",
        query_fn=query_anthropic_model_with_retry,
        output_dir=out_base
    )

    # Save combined results
    combined = {
        "gpt-5.6-sol": gpt_results,
        "claude-fable-5": claude_results
    }
    with open(f"{out_base}/frontier_models_combined_results.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)

    print("\n" + "=" * 110)
    print("                      FRONTIER MODEL MULTI-CONDITION BENCHMARK SUMMARY")
    print("=" * 110)
    print(f"{'Model':<18} | {'Condition':<35} | {'Peak RAM':<12} | {'Time (s)':<10} | {'128MB Sandbox Status':<18}")
    print("-" * 110)
    for m_name, res_dict in combined.items():
        for cond_name, v in res_dict.items():
            p = v["profile"]
            if not p["success"]:
                sandbox_stat = "❌ TIMEOUT/ERROR"
            elif p["peak_mb"] > 128.0:
                sandbox_stat = f"💥 OOM ({p['peak_mb']:.1f}MB)"
            else:
                sandbox_stat = "✅ PASS"
            print(f"{m_name:<18} | {cond_name:<35} | {p['peak_mb']:<8.2f} MB | {p['wall_sec']:<10.4f} | {sandbox_stat:<18}")
        print("-" * 110)

if __name__ == "__main__":
    main()
