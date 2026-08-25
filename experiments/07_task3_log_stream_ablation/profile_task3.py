import os
import sys
import time
import tracemalloc
import subprocess
import shutil
import tempfile

out_dir = "experiments/07_task3_log_stream_ablation"
os.makedirs(f"{out_dir}/runs", exist_ok=True)

# 1. Variant A (Blind) Code
code_a = """import sys
from collections import Counter

def process_logs(file_path='server_logs.txt'):
    server_errors = 0
    endpoint_counts = Counter()
    unique_ips = set()

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 7:
                    continue
                
                ip = parts[1]
                endpoint = parts[3]
                status_str = parts[4]
                
                try:
                    status = int(status_str)
                    if 500 <= status < 600:
                        server_errors += 1
                except ValueError:
                    pass
                
                endpoint_counts[endpoint] += 1
                unique_ips.add(ip)
    except FileNotFoundError:
        pass

    top_5 = [ep for ep, _ in endpoint_counts.most_common(5)]
    top_endpoints_str = ",".join(top_5)

    print(f"ERRORS:{server_errors}")
    print(f"TOP_ENDPOINTS:{top_endpoints_str}")
    print(f"UNIQUE_IPS:{len(unique_ips)}")

if __name__ == '__main__':
    process_logs()
"""

# 2. Variant B (Natural Language) Code
code_b = """import sys
from collections import Counter

def process_logs(filepath: str = "server_logs.txt") -> None:
    error_5xx_count = 0
    endpoint_counts = Counter()
    unique_ips = set()

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue

                ip = parts[1]
                endpoint = parts[3]
                status_code = parts[4]

                unique_ips.add(ip)
                endpoint_counts[endpoint] += 1

                try:
                    code = int(status_code)
                    if 500 <= code < 600:
                        error_5xx_count += 1
                except ValueError:
                    pass
    except FileNotFoundError:
        pass

    top_5_endpoints = [ep for ep, _ in endpoint_counts.most_common(5)]
    top_endpoints_str = ",".join(top_5_endpoints)

    print(f"ERRORS:{error_5xx_count}")
    print(f"TOP_ENDPOINTS:{top_endpoints_str}")
    print(f"UNIQUE_IPS:{len(unique_ips)}")

if __name__ == "__main__":
    process_logs()
"""

# 3. Variant C (1D Telemetry: RAM 64 MB) Code
code_c = """import collections
import tempfile

def process_logs(file_path: str = "server_logs.txt") -> None:
    errors = 0
    endpoint_counts = collections.Counter()

    num_shards = 32
    shard_files = [
        tempfile.TemporaryFile(mode="w+", encoding="utf-8", buffering=65536)
        for _ in range(num_shards)
    ]

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue

                ip = parts[1]
                endpoint = parts[3]
                status_str = parts[4]

                try:
                    status = int(status_str)
                    if 500 <= status < 600:
                        errors += 1
                except ValueError:
                    pass

                endpoint_counts[endpoint] += 1

                shard_idx = hash(ip) % num_shards
                shard_files[shard_idx].write(ip + "\\n")

        unique_ips = 0
        for shard_file in shard_files:
            shard_file.seek(0)
            seen_ips = set()
            for ip_line in shard_file:
                seen_ips.add(ip_line.rstrip("\\n"))
            unique_ips += len(seen_ips)
            seen_ips.clear()

    finally:
        for shard_file in shard_files:
            shard_file.close()

    top_5_endpoints = [ep for ep, _ in endpoint_counts.most_common(5)]

    print(f"ERRORS:{errors}")
    print(f"TOP_ENDPOINTS:{','.join(top_5_endpoints)}")
    print(f"UNIQUE_IPS:{unique_ips}")

if __name__ == "__main__":
    process_logs("server_logs.txt")
"""

# 4. Variant D (2D Telemetry: RAM 64 MB, Time 5.0s) Code
code_d = """from collections import Counter
import sys

def process_logs(filename='server_logs.txt'):
    error_5xx_count = 0
    endpoint_counts = Counter()
    unique_ips = set()

    with open(filename, 'r', encoding='utf-8', errors='ignore', buffering=1024 * 1024) as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 5:
                ip = parts[1]
                endpoint = parts[3]
                status = parts[4]

                unique_ips.add(ip)
                endpoint_counts[endpoint] += 1

                if '500' <= status < '600':
                    error_5xx_count += 1

    top_5_endpoints = [endpoint for endpoint, _ in endpoint_counts.most_common(5)]

    print(f"ERRORS:{error_5xx_count}")
    print(f"TOP_ENDPOINTS:{','.join(top_5_endpoints)}")
    print(f"UNIQUE_IPS:{len(unique_ips)}")

if __name__ == '__main__':
    log_file = sys.argv[1] if len(sys.argv) > 1 else 'server_logs.txt'
    process_logs(log_file)
"""

variants = {
    "Variant A (Blind)": code_a,
    "Variant B (Natural Language)": code_b,
    "Variant C (1D Telemetry: 64M RAM)": code_c,
    "Variant D (2D Telemetry: 64M RAM + 5s Time)": code_d
}

def profile_code(code_str: str) -> dict:
    sandbox = tempfile.mkdtemp(prefix="task3_eval_")
    script_path = os.path.join(sandbox, "run.py")
    src = os.path.abspath("data/server_logs.txt")
    dst = os.path.join(sandbox, "server_logs.txt")
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
            "success": err_flag == 0 and "UNIQUE_IPS:" in stdout,
            "stdout": stdout.strip()[:300],
            "stderr": stderr.strip()[:300]
        }
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

print("=" * 95)
print(f"{'Condition':<40} | {'Peak RAM':<12} | {'Time (s)':<10} | {'Algorithmic Strategy':<25}")
print("=" * 95)

for k, code in variants.items():
    safe_name = k.split(" ")[1].replace("(", "").replace(")", "").lower()
    script_file = f"{out_dir}/runs/{safe_name}_gemini-3.7-flash.py"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(code)
    
    prof = profile_code(code)
    strat = "External Disk Sharding" if "shard" in code else "In-Memory Set/Counter"
    print(f"{k:<40} | {prof['peak_mb']:<8.2f} MB | {prof['wall_sec']:<10.4f} | {strat:<25}")
print("=" * 95)
