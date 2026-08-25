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
model_id = "gpt-5.6-sol"

prompt = """Write a self-contained, executable Python script to process 'vectors.npy' (containing an 8,000 x 1,024 float32 matrix).
Compute the total sum of all pairwise Euclidean distances between rows: sum_{i,j} ||v_i - v_j||_2 and print: 'TOTAL_DIST:<value>'.
Constraint: Use ONLY numpy and standard library modules. Do NOT import scipy or external packages.

Execution environment:
RAM limit: 128 MB.
Execution time limit: 10.0 seconds."""

print(f"[*] Querying {model_id}...")
url = "https://api.openai.com/v1/chat/completions"
req_data = {
    "model": model_id,
    "messages": [{"role": "user", "content": prompt}]
}
req = urllib.request.Request(
    url,
    headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
    data=json.dumps(req_data).encode("utf-8")
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        raw = data["choices"][0]["message"]["content"]
        print(f"[+] Successfully received response from {model_id}!")
except Exception as e:
    print(f"[!] Query failed: {e}")
    sys.exit(1)

raw_str = raw.strip()
if "```python" in raw_str:
    code = raw_str.split("```python")[1].split("```")[0].strip()
elif "```py" in raw_str:
    code = raw_str.split("```py")[1].split("```")[0].strip()
elif "```" in raw_str:
    code = raw_str.split("```")[1].split("```")[0].strip()
else:
    code = raw_str

os.makedirs("./local_experiments/openai_benchmark/runs", exist_ok=True)
script_out = "./local_experiments/openai_benchmark/runs/2d_gpt-5.6-sol.py"
with open(script_out, "w", encoding="utf-8") as f:
    f.write(code)

print("=" * 80)
print(f"GENERATED CODE FROM {model_id}:")
print("=" * 80)
print(code)
print("=" * 80)

# Profile locally
sandbox = tempfile.mkdtemp(prefix="sol_run_")
script_path = os.path.join(sandbox, "run.py")
src = os.path.abspath("./foil_data/vectors.npy")
dst = os.path.join(sandbox, "vectors.npy")
try:
    os.symlink(src, dst)
except OSError:
    shutil.copy2(src, dst)

with open(script_path, "w", encoding="utf-8") as f:
    f.write(code)

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
    print("\nPROFILING EXECUTION RESULT:")
    print("STDOUT:", proc.stdout.strip())
    if proc.stderr:
        print("STDERR:", proc.stderr.strip())
finally:
    shutil.rmtree(sandbox, ignore_errors=True)
