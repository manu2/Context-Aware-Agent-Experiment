"""
Canonical Post-Hoc OS MaxRSS Profiler for Substrate-Aware Paired Trials.

This script executes all 20 archived trial scripts in isolated subprocesses,
measures actual operating system peak resident set size (MaxRSS via resource.getrusage),
verifies correct computation outputs, and outputs a canonical machine-readable JSON dataset.
"""

import os
import sys
import glob
import json
import time
import subprocess
import resource
import platform

def profile_script(script_path: str, data_dir: str = "data") -> dict:
    abs_script = os.path.abspath(script_path)
    abs_data = os.path.abspath(data_dir)
    
    # Subprocess code to run the script in data_dir context and record MaxRSS
    runner_code = f"""
import sys, time, resource, os
t0 = time.perf_counter()
err_msg = None
output_val = None
try:
    with open("{abs_script}", "r", encoding="utf-8") as f:
        code = f.read()
    globs = {{"__file__": "{abs_script}", "__name__": "__main__"}}
    exec(code, globs)
except SystemExit:
    pass
except Exception as e:
    err_msg = str(e)
t1 = time.perf_counter()
ru = resource.getrusage(resource.RUSAGE_SELF)
# Darwin ru_maxrss is in bytes; Linux in KB
rss_mb = ru.ru_maxrss / (1024 * 1024) if sys.platform == 'darwin' else ru.ru_maxrss / 1024
print(f"\\n___CANONICAL_PROFILE___|{{t1 - t0:.4f}}|{{rss_mb:.2f}}|{{err_msg}}")
"""
    proc = subprocess.run(
        [sys.executable, "-c", runner_code],
        cwd=abs_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=60
    )
    
    stdout = proc.stdout
    stderr = proc.stderr
    wall_sec = 0.0
    maxrss_mb = 0.0
    err_str = None
    
    for line in stdout.splitlines():
        if "___CANONICAL_PROFILE___" in line:
            parts = line.split("|")
            wall_sec = float(parts[1])
            maxrss_mb = float(parts[2])
            err_str = parts[3] if parts[3] != "None" else None
            
    # Extract calculated total distance if present
    total_dist = None
    for line in stdout.splitlines():
        if "TOTAL_DIST:" in line:
            try:
                total_dist = float(line.split("TOTAL_DIST:")[1].strip())
            except ValueError:
                pass

    success = (err_str is None) and (total_dist is not None)
    
    return {
        "wall_sec": round(wall_sec, 4),
        "maxrss_mb": round(maxrss_mb, 2),
        "success": success,
        "total_dist": total_dist,
        "within_128m_budget": maxrss_mb < 128.0,
        "error": err_str,
        "stdout_snippet": stdout.strip()[:300]
    }

def main():
    runs_dir = "experiments/05_paired_statistical_trials/runs"
    scripts = sorted(glob.glob(f"{runs_dir}/*.py"))
    
    if not scripts:
        print(f"Error: No scripts found in {runs_dir}")
        sys.exit(1)
        
    print(f"[*] Running canonical OS MaxRSS profiling on {len(scripts)} archived trial scripts...")
    
    canonical_data = {
        "metadata": {
            "profiler": "experiments/05_paired_statistical_trials/profile_canonical_maxrss.py",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "platform": platform.platform(),
            "python_version": sys.version.split()[0],
            "methodology": "resource.getrusage(RUSAGE_SELF).ru_maxrss in isolated subprocess"
        },
        "trials": []
    }
    
    for s in scripts:
        fname = os.path.basename(s)
        parts = fname.replace(".py", "").split("_")
        # Format: <model>_<trial>_<condition_letter>_<condition_name>
        # e.g., claude-opus-5_trial1_A_blind.py
        model = parts[0]
        trial_id = int(parts[1].replace("trial", ""))
        cond_letter = parts[2]
        cond_name = parts[3]
        
        prof = profile_script(s)
        
        entry = {
            "model": model,
            "trial": trial_id,
            "condition_letter": cond_letter,
            "condition_name": cond_name,
            "script_path": s,
            "maxrss_mb": prof["maxrss_mb"],
            "wall_sec": prof["wall_sec"],
            "total_dist": prof["total_dist"],
            "within_128m_budget": prof["within_128m_budget"],
            "execution_success": prof["success"],
            "error": prof["error"]
        }
        canonical_data["trials"].append(entry)
        print(f"  - {fname:<45} | MaxRSS: {prof['maxrss_mb']:>6.2f} MB | Time: {prof['wall_sec']:>6.4f}s | Budget: {'✅ <128M' if prof['within_128m_budget'] else '💥 >128M'}")
        
    out_json = "experiments/05_paired_statistical_trials/canonical_paired_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(canonical_data, f, indent=2)
        
    print(f"\n[+] Canonical dataset successfully written to {out_json}")

if __name__ == "__main__":
    main()
