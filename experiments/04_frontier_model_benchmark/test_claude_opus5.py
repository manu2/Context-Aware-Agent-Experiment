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

prompt = """Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages.

Execution environment:
RAM limit: 128 MB.
Execution time limit: 10.0 seconds."""

print(f"[*] Querying {model_id} with max_tokens=8192...")
req_data = {
    "model": model_id,
    "max_tokens": 8192,
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

with urllib.request.urlopen(req, timeout=180) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    print("Stop reason:", res.get("stop_reason"))
    content = res.get("content", [])
    text = "".join([b.get("text", "") for b in content if b.get("type") == "text"])

raw_str = text.strip()
if "```python" in raw_str:
    code = raw_str.split("```python")[1].split("```")[0].strip()
elif "```py" in raw_str:
    code = raw_str.split("```py")[1].split("```")[0].strip()
elif "```" in raw_str:
    code = raw_str.split("```")[1].split("```")[0].strip()
else:
    code = raw_str

print("=" * 80)
print("FULL GENERATED CODE:")
print("=" * 80)
print(code)
print("=" * 80)

os.makedirs("./local_experiments/frontier_model_benchmark/runs", exist_ok=True)
with open("./local_experiments/frontier_model_benchmark/runs/2d_claude-opus-5.py", "w") as f:
    f.write(code)

sandbox = tempfile.mkdtemp(prefix="opus5_run_")
script_path = os.path.join(sandbox, "run.py")
shutil.copy2("./foil_data/vectors.npy", os.path.join(sandbox, "vectors.npy"))
with open(script_path, "w") as f:
    f.write(code)

wrapper = f"""
import sys, time, tracemalloc
tracemalloc.start()
t0 = time.perf_counter()
with open("{script_path}") as f:
    exec(f.read(), {{'__file__': '{script_path}', '__name__': '__main__'}})
t1 = time.perf_counter()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"\\n___PROFILE_RESULT___|{{t1 - t0:.4f}}|{{peak / 1024 / 1024:.2f}}|0")
"""
proc = subprocess.run([sys.executable, "-c", wrapper], cwd=sandbox, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
print("EXECUTION PROFILE RESULT:")
print(proc.stdout.strip())
if proc.stderr:
    print("STDERR:", proc.stderr.strip())
shutil.rmtree(sandbox, ignore_errors=True)
