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

def clean_code(raw: str) -> str:
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


def query_openai(prompt: str, model_id: str = "gpt-5.6-sol", max_retries: int = 3) -> str:
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
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw = data["choices"][0]["message"]["content"]
                return clean_code(raw)
        except Exception as e:
            print(f"    [!] Attempt {attempt}/{max_retries} failed ({e}), retrying in 3s...", flush=True)
            time.sleep(3)
    raise RuntimeError(f"OpenAI {model_id} failed after {max_retries} retries.")


def profile_code(code_str: str, data_dir: str = "./foil_data") -> dict:
    sandbox = tempfile.mkdtemp(prefix="gpt_eval_")
    script_path = os.path.join(sandbox, "run.py")

    src = os.path.abspath(os.path.join(data_dir, "vectors.npy"))
    dst = os.path.join(sandbox, "vectors.npy")
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
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def main():
    model_name = "gpt-5.6-sol"
    output_dir = "./local_experiments/paired_trials"
    os.makedirs(f"{output_dir}/runs", exist_ok=True)
    
    base_task = (
        "Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).\n"
        "Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.\n"
        "Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."
    )
    prompt_a = base_task
    prompt_d = f"{base_task}\n\nExecution environment:\nRAM limit: 128 MB.\nExecution time limit: 10.0 seconds."

    json_file = f"{output_dir}/gpt-5.6-sol_5_paired_trials.json"
    results = []

    for trial_idx in range(1, 6):
        print(f"[*] Running GPT-5.6-Sol Trial {trial_idx}/5...", flush=True)
        # Variant A
        print(f"    -> Querying Condition A (Blind)...", flush=True)
        code_a = query_openai(prompt_a, model_id=model_name)
        file_a = f"{output_dir}/runs/gpt-5.6-sol_trial{trial_idx}_A_blind.py"
        with open(file_a, "w", encoding="utf-8") as f:
            f.write(code_a)
        prof_a = profile_code(code_a)
        print(f"       Blind: {prof_a['peak_mb']:.2f} MB | {prof_a['wall_sec']:.4f}s", flush=True)

        time.sleep(1.0)

        # Variant D
        print(f"    -> Querying Condition D (2D Telemetry)...", flush=True)
        code_d = query_openai(prompt_d, model_id=model_name)
        file_d = f"{output_dir}/runs/gpt-5.6-sol_trial{trial_idx}_D_2Dtelemetry.py"
        with open(file_d, "w", encoding="utf-8") as f:
            f.write(code_d)
        prof_d = profile_code(code_d)
        print(f"       2D Telemetry: {prof_d['peak_mb']:.2f} MB | {prof_d['wall_sec']:.4f}s", flush=True)

        results.append({
            "trial": trial_idx,
            "A_Blind": {"code_path": file_a, "profile": prof_a},
            "D_2DTelemetry": {"code_path": file_d, "profile": prof_d}
        })
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        time.sleep(1.5)

    print(f"\n[+] Successfully finished 5 paired trials for {model_name}!", flush=True)


if __name__ == "__main__":
    main()
