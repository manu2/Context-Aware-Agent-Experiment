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
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw = data["choices"][0]["message"]["content"]
                return clean_code(raw)
        except Exception as e:
            print(f"    [!] OpenAI attempt {attempt}/{max_retries} failed ({e}), retrying...")
            time.sleep(5)
    raise RuntimeError(f"OpenAI {model_id} failed after {max_retries} retries.")


def query_anthropic(prompt: str, model_id: str = "claude-opus-5", max_retries: int = 3) -> str:
    url = "https://api.anthropic.com/v1/messages"
    req_data = {
        "model": model_id,
        "max_tokens": 8192,
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
                content = data.get("content", [])
                text = "".join([b.get("text", "") for b in content if b.get("type") == "text"])
                return clean_code(text)
        except Exception as e:
            print(f"    [!] Anthropic attempt {attempt}/{max_retries} failed ({e}), retrying...")
            time.sleep(5)
    raise RuntimeError(f"Anthropic {model_id} failed after {max_retries} retries.")


def profile_code(code_str: str, data_dir: str = "./foil_data") -> dict:
    sandbox = tempfile.mkdtemp(prefix="paired_eval_")
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


def run_paired_trials_for_model(model_name: str, query_fn, num_trials: int = 5, output_dir: str = "./local_experiments/paired_trials"):
    os.makedirs(f"{output_dir}/runs", exist_ok=True)
    base_task = (
        "Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).\n"
        "Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.\n"
        "Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages."
    )

    conditions = {
        "A_Blind": base_task,
        "D_2DTelemetry": f"{base_task}\n\nExecution environment:\nRAM limit: 128 MB.\nExecution time limit: 10.0 seconds."
    }

    results = []
    print(f"\n===================================================================================")
    print(f"  RUNNING {num_trials} PAIRED TRIALS FOR MODEL: {model_name.upper()}")
    print(f"===================================================================================\n")

    for trial_idx in range(1, num_trials + 1):
        print(f"--- [Trial {trial_idx}/{num_trials}] ---")
        trial_record = {"trial": trial_idx}

        # 1. Run Condition A (Blind)
        print(f"[*] [{model_name}] Querying Condition A (Blind)...")
        code_a = query_fn(conditions["A_Blind"], model_id=model_name)
        file_a = f"{output_dir}/runs/{model_name}_trial{trial_idx}_A_blind.py"
        with open(file_a, "w", encoding="utf-8") as f:
            f.write(code_a)
        prof_a = profile_code(code_a)
        stat_a = "💥 OOM (>128M)" if prof_a["peak_mb"] > 128.0 or not prof_a["success"] else "✅ PASS"
        print(f"    -> Blind: Peak RAM={prof_a['peak_mb']:.2f} MB | Latency={prof_a['wall_sec']:.4f}s | {stat_a}")
        trial_record["A_Blind"] = {"code_path": file_a, "profile": prof_a}

        time.sleep(1.5)

        # 2. Run Condition D (2D Telemetry)
        print(f"[*] [{model_name}] Querying Condition D (2D Telemetry)...")
        code_d = query_fn(conditions["D_2DTelemetry"], model_id=model_name)
        file_d = f"{output_dir}/runs/{model_name}_trial{trial_idx}_D_2Dtelemetry.py"
        with open(file_d, "w", encoding="utf-8") as f:
            f.write(code_d)
        prof_d = profile_code(code_d)
        stat_d = "💥 OOM (>128M)" if prof_d["peak_mb"] > 128.0 or not prof_d["success"] else "✅ PASS"
        print(f"    -> 2D Telemetry: Peak RAM={prof_d['peak_mb']:.2f} MB | Latency={prof_d['wall_sec']:.4f}s | {stat_d}")
        trial_record["D_2DTelemetry"] = {"code_path": file_d, "profile": prof_d}

        results.append(trial_record)
        time.sleep(2.0)

    json_file = f"{output_dir}/{model_name}_5_paired_trials.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Paired trials complete for {model_name}. Saved to {json_file}")
    return results


def main():
    os.makedirs("./foil_data", exist_ok=True)
    os.makedirs("./local_experiments/paired_trials", exist_ok=True)
    npy_file = "./foil_data/vectors.npy"
    if not os.path.exists(npy_file):
        print("[*] Generating synthetic vectors.npy (8000 x 1024 float32, ~32.8MB)...")
        np.random.seed(42)
        mat = np.random.randn(8000, 1024).astype(np.float32)
        np.save(npy_file, mat)

    out_dir = "./local_experiments/paired_trials"

    # 1. Run 5 paired trials on Claude Opus 5
    opus_trials = run_paired_trials_for_model(
        model_name="claude-opus-5",
        query_fn=query_anthropic,
        num_trials=5,
        output_dir=out_dir
    )

    # 2. Run 5 paired trials on GPT-5.6-Sol
    gpt_trials = run_paired_trials_for_model(
        model_name="gpt-5.6-sol",
        query_fn=query_openai,
        num_trials=5,
        output_dir=out_dir
    )

    print("\n" + "=" * 105)
    print("                    STATISTICAL 5-PAIRED TRIAL BENCHMARK SUMMARY")
    print("=" * 105)
    print(f"{'Model':<18} | {'Trial':<6} | {'Blind Peak RAM':<16} | {'Aware Peak RAM':<16} | {'Delta RAM':<12} | {'Aware Pass?':<12}")
    print("-" * 105)
    
    for m_name, trial_data in [("claude-opus-5", opus_trials), ("gpt-5.6-sol", gpt_trials)]:
        blind_rams = []
        aware_rams = []
        for t in trial_data:
            r_a = t["A_Blind"]["profile"]["peak_mb"]
            r_d = t["D_2DTelemetry"]["profile"]["peak_mb"]
            blind_rams.append(r_a)
            aware_rams.append(r_d)
            delta = r_a - r_d
            pass_str = "✅ PASS" if r_d <= 128.0 and t["D_2DTelemetry"]["profile"]["success"] else "💥 FAIL"
            print(f"{m_name:<18} | {t['trial']:<6} | {r_a:<10.2f} MB       | {r_d:<10.2f} MB       | -{delta:<9.2f} MB| {pass_str:<12}")
        
        mean_a = np.mean(blind_rams)
        std_a = np.std(blind_rams)
        mean_d = np.mean(aware_rams)
        std_d = np.std(aware_rams)
        print(f"--> {m_name} MEAN: Blind = {mean_a:.2f} ± {std_a:.2f} MB  ||  Aware = {mean_d:.2f} ± {std_d:.2f} MB")
        print("-" * 105)

if __name__ == "__main__":
    main()
