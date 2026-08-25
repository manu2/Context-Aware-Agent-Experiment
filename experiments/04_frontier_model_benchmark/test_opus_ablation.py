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

model_id = "claude-opus-5"
url = "https://api.anthropic.com/v1/messages"

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
    }
}

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

def query_opus(prompt_text):
    req_data = {
        "model": model_id,
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": prompt_text}]
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
    with urllib.request.urlopen(req, timeout=180) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        content = res.get("content", [])
        text = "".join([b.get("text", "") for b in content if b.get("type") == "text"])
        return clean_code(text)

def profile_script(code_str):
    sandbox = tempfile.mkdtemp(prefix="eval_opus_")
    script_path = os.path.join(sandbox, "run.py")
    shutil.copy2("./foil_data/vectors.npy", os.path.join(sandbox, "vectors.npy"))
    with open(script_path, "w") as f:
        f.write(code_str)

    wrapper = f"""
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
    proc = subprocess.run([sys.executable, "-c", wrapper], cwd=sandbox, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    shutil.rmtree(sandbox, ignore_errors=True)
    
    wall_sec = 0.0
    peak_mb = 0.0
    err_flag = 0
    for line in proc.stdout.splitlines():
        if "___PROFILE_RESULT___" in line:
            parts = line.split("|")
            wall_sec = float(parts[1])
            peak_mb = float(parts[2])
            err_flag = int(parts[3])
    return {
        "wall_sec": wall_sec,
        "peak_mb": peak_mb,
        "success": err_flag == 0 and "TOTAL_DIST:" in proc.stdout,
        "stdout": proc.stdout.strip()[:300],
        "stderr": proc.stderr.strip()[:300]
    }

results = {}
for k, v in variants.items():
    print(f"[*] Querying {model_id} for {k}...")
    code = query_opus(v["prompt"])
    safe = k.split(" ")[1].replace("(", "").replace(")", "").lower()
    out_file = f"./local_experiments/frontier_model_benchmark/runs/{safe}_{model_id}.py"
    with open(out_file, "w") as f:
        f.write(code)
    print(f"    Saved -> {out_file}")
    prof = profile_script(code)
    print(f"    Result: Peak RAM={prof['peak_mb']:.2f} MB | Latency={prof['wall_sec']:.4f}s | Success={prof['success']}")
    results[k] = {"code": code, "profile": prof}
    time.sleep(2.0)

print("\n" + "=" * 90)
print(f"{'Condition':<40} | {'Peak RAM':<12} | {'Time (s)':<10} | {'128MB Status':<15}")
print("-" * 90)
for k, v in results.items():
    p = v["profile"]
    stat = "💥 OOM (215MB+)" if p["peak_mb"] > 128.0 else "✅ PASS"
    print(f"{k:<40} | {p['peak_mb']:<8.2f} MB | {p['wall_sec']:<10.4f} | {stat:<15}")
print("=" * 90)
