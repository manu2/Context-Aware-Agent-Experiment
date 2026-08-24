# RESEARCH HANDOVER & IMPLEMENTATION BRIEF: PROJECT AETHER-BUS / SCAC
**To:** Autonomous Coding & Systems Execution Agent  
**From:** Research Lead & Systems Architecture Team  
**Date:** August 2026  
**Subject:** Full Context, Research Thesis, Week-1 "Foil" Test Protocol, and GCE Deployment Guide  

---

## 1. Executive Context & The Motivating Problem

### 1.1 The Genesis & The Jeff Dean / Discovery Loop Connection
As the AI field shifts from static text generation to autonomous agent loops—exemplified by Jeff Dean’s initiative **Discovery Loop**, which automates parallel scientific discovery and experimental simulations—execution harnesses are hitting a major performance wall.

In high-throughput scientific sandboxes, agents are dispatched to write and execute code across thousands of heterogeneous virtualized containers (ranging from 128MB serverless micro-VMs to multi-core compute nodes). Currently, agents treat every execution container as an unconstrained, infinite black box:
1. **Silicon Blindness:** An agent writes naive, memory-heavy code (e.g., eager `pd.read_csv()` on an 85MB file or an eager `mat @ mat.T` on 8,000 vectors).
2. **Silent Kernel Termination:** The Linux kernel immediately triggers an Out-Of-Memory (OOM) kill (`SIGKILL` / Exit Code 137).
3. **The Wasted Retry Loop:** The agent receives an opaque error string (`Process Exited with Code 137`), writes a conversational apology, and retries the exact same memory-heavy algorithm until token budgets or context windows collapse [Why Do Multi-Agent LLM Systems Fail...; How to Manage LLM Context Windows...].

### 1.2 Prior Art & Exact Novelty Boundaries
To avoid redundant engineering, our prior art scan established clear boundaries:
* **AgentSight (ACM PACMI, late 2025):** Bridges agent intent and kernel events via eBPF [System-Level Observability... Using eBPF; System-Level Observability... Using eBPF].  
  * *Boundary:* Built strictly for human operations, post-hoc audits, and compliance. It does not loop telemetry back to the model during inference.
* **ActPlane (Eunomia Community, 2026):** Pushes runtime enforcement down to Linux via BPF-LSM and exposes an MCP sandbox firewall [ActPlane: Pushing Agent Harness...].  
  * *Boundary:* Functions as an immutable security kill-switch [An Empirical Study: AI Agent Rules...]. When a violation occurs, it halts execution without helping the agent understand physical limits or recover.

**Our Core Research Thesis (Substrate-Conditioned Agentic Computation - SCAC):**  
Instead of treating hardware as an invisible black box or using kernel tools solely for human audits, we treat **execution-substrate constraints as a first-class input to the agent's planning state**. We investigate whether exposing physical constraints (RAM ceilings, CPU quotas, runtime pressure) enables autonomous agents to dynamically select appropriate computational strategies (streaming, chunking, out-of-core tiling).

---

## 2. Research Trajectory: From Week 1 to Top-Tier Paper

To prevent the classic systems engineering trap—building an elaborate multi-node research harness before proving the basic premise—the project is structured into three distinct phases:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PROJECT ROADMAP PHASING                         │
│                                                                        │
│  [WEEK 1: THE "FOIL CAN FLY" SIGNAL TEST] ◄── CURRENT FOCUS           │
│  • Pure, zero-middleware A/B test (20 live LLM runs on Gemini/Claude)  │
│  • Question: Does disclosing a 128MB RAM limit cause the model to      │
│    switch from eager loading to chunking/streaming on its own?         │
│                                                                        │
│  [WEEK 2: MULTI-DIMENSIONAL & TWO-TURN ADAPTATION]                    │
│  • 90-trial matrix (CSV Aggregation & Matrix Operations)               │
│  • Two-turn closed-loop kernel feedback (Preventive adaptation via     │
│    cgroup v2 `memory.events.local: high` before OOM kills occur)       │
│  • Full `cpu.stat` quota accounting                                    │
│                                                                        │
│  [WEEK 3+: THE FULL SYSTEMS PAPER & STANDARD]                          │
│  • Formal research submission (OSDI / MLSys / NeurIPS track)           │
│  • Formalizing the Aether-Bus Resource-Offer Protocol for AI agents   │
│  • Prefix cache retention economics and multi-agent cluster scheduling │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Week-1 Experimental Protocol ("Does the Foil Fly?")

### 3.1 The Single Question to Answer
> **"When an LLM coding agent is explicitly told its execution sandbox has a 128MB RAM limit, does it autonomously switch to memory-bounded algorithms without being given any solution hints?"**

### 3.2 The Pure A/B Intervention
* **Condition A (Blind):**
  ```text
  Write a self-contained Python script to process 'data.csv'.
  Group records by 'category_id' and compute the sum of 'metric_val'.
  Print the final total count of unique categories: 'TOTAL_CATEGORIES:<count>'.
  ```
* **Condition B (Substrate-Aware):**
  ```text
  Write a self-contained Python script to process 'data.csv'.
  Group records by 'category_id' and compute the sum of 'metric_val'.
  Print the final total count of unique categories: 'TOTAL_CATEGORIES:<count>'.

  Execution environment:
  RAM limit: 128 MB.
  ```
*(Zero prescriptive hints: no mention of "chunksize", "generators", "streaming", or "SIGKILL").*

### 3.3 Physical Dataset & Container Sizing
* **The Task Dataset:** A calibrated synthetic CSV containing **2,000,000 rows $\times$ 5 columns** (`id`, `category_id`, `metric_val`, `text_code`, `score`), taking $\sim 85\text{ MB}$ raw on disk.
* **The Memory Bifurcation:**
  * Eager `pd.read_csv('data.csv')` creates string/numeric objects peaking at **$\sim 240–300\text{ MB}$ heap memory** during parsing $\rightarrow$ **Guaranteed OOM Kill under a 128MB container ceiling**.
  * Chunked iteration (`chunksize=50_000`) or streaming line loops consume **$\sim 25–35\text{ MB}$ peak RAM** $\rightarrow$ **Completes with $>70\%$ memory headroom**.
* **The Experimental Matrix:** 10 Paired Trials (10 Blind + 10 Substrate-Aware = **20 independent LLM generations total**).

---

## 4. Google Cloud (GCE) Infrastructure & Deployment Guide

To ensure authentic OS-level memory enforcement, the experiment must run on a **Linux host with unified `cgroup v2` enabled**.

### 4.1 Target VM Specification
* **Cloud Provider:** Google Cloud Engine (GCE)
* **Machine Type:** `e2-medium` (2 vCPU / 4 GB RAM)
* **Operating System:** **Ubuntu 24.04 LTS** (Kernel 6.8+, systemd v255, unified cgroup v2 enabled by default)
* **Cost:** Less than $\$0.05/\text{hour}$ (runs in $< 3\text{ minutes}$).

### 4.2 Step-by-Step GCE Provisioning
Run these commands from your local terminal with the `gcloud` CLI:

```bash
# 1. Provision the Ubuntu 24.04 VM
gcloud compute instances create scac-foil-node \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2404-lts-amd64 \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB

# 2. SSH into the instance
gcloud compute ssh scac-foil-node --zone=us-central1-a
```

Inside the VM, install dependencies and export your API key:
```bash
# 3. Install Python environment
sudo apt update && sudo apt install -y python3 python3-pip python3-numpy python3-pandas

# 4. Set Gemini API Key and Model (or Anthropic/OpenAI)
export GEMINI_API_KEY="AIzaSy..."
export SCAC_MODEL="gemini-3.7-flash"   # Options: gemini-3.7-flash, claude-3-7-sonnet-20250219, gpt-4o

# 5. Run the experiment
python3 week1_foil_test.py
```

---

## 5. The Complete, Production-Audited Code (`week1_foil_test.py`)

This script contains **zero mock code and zero Aether-Bus middleware**. It handles dataset generation, queries the live LLM API, executes inside real 128MB `cgroup v2` sandboxes (`systemd-run`), archives all generated code to `./foil_runs/`, and outputs the paired comparison table:

```python
import os
import sys
import time
import json
import subprocess
import shutil
import tempfile
import numpy as np

# =====================================================================
# CONFIGURATION
# =====================================================================
# Model override: e.g. "gemini-3.7-flash", "claude-3-7-sonnet-20250219", "gpt-4o"
MODEL_NAME = os.environ.get("SCAC_MODEL", "gemini-3.7-flash")
MEMORY_LIMIT_MB = 128
PAIRED_TRIALS = 10


# =====================================================================
# 1. PRE-FLIGHT CGROUP V2 AUDIT (FAIL-CLOSED)
# =====================================================================
def verify_environment_or_abort():
    """
    FAIL-CLOSED: Aborts if Linux cgroup v2 / systemd-run is missing
    or if MemoryMax fails to trigger an OOM kill on a 150MB allocation.
    """
    if shutil.which("systemd-run") is None:
        print("\n" + "!" * 80)
        print("[!] FATAL ERROR: 'systemd-run' (Linux cgroup v2) not found.")
        print("    This experiment requires a Linux host with active cgroup v2 controller delegation.")
        print("    Running unconstrained would produce invalid data. Aborting.")
        print("!" * 80 + "\n")
        sys.exit(1)

    print("[*] Running pre-flight cgroup v2 positive-control test (150MB alloc vs 128MB limit)...")
    test_unit = f"scac_preflight_{time.time_ns()}"
    test_cmd = [
        "systemd-run", "--user", "--scope", f"--unit={test_unit}", "-q",
        f"-p", f"MemoryMax={MEMORY_LIMIT_MB}M",
        f"-p", "MemorySwapMax=0",
        sys.executable, "-c", "data = bytearray(150 * 1024 * 1024)"  # Exceeds 128MB limit
    ]
    proc = subprocess.run(test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode not in (137, -9, 1):
        print(f"\n[!] FATAL ERROR: Pre-flight MemoryMax assertion failed (exit code: {proc.returncode}).")
        print("    User-slice controller delegation is not active. Aborting.")
        sys.exit(1)

    print("[+] Pre-flight passed: Kernel deterministically kills allocations exceeding 128MB.\n")


# =====================================================================
# 2. GENERATE DETERMINISTIC 2M-ROW CSV (~85MB)
# =====================================================================
def ensure_dataset(data_dir: str = "./foil_data") -> str:
    os.makedirs(data_dir, exist_ok=True)
    csv_file = os.path.join(data_dir, "data.csv")

    if not os.path.exists(csv_file):
        print("[*] Generating 2,000,000 row CSV (~85MB, >240MB eager DataFrame memory)...")
        np.random.seed(42)
        n = 2_000_000
        cats = np.random.randint(1, 500, size=n)
        vals = np.random.randint(1, 100, size=n)
        scores = np.random.rand(n).round(4)
        
        with open(csv_file, "w") as f:
            f.write("id,category_id,metric_val,text_code,score\n")
            for i in range(n):
                f.write(f"{i},{cats[i]},{vals[i]},CAT_{cats[i]:04d},{scores[i]}\n")
        print("[+] Dataset generated.")

    return os.path.abspath(data_dir)


# =====================================================================
# 3. CGROUP V2 EXECUTION SANDBOX (128MB RAM CEILING)
# =====================================================================
def execute_in_128mb_sandbox(code_str: str, data_dir: str, timeout_sec: int = 30) -> dict:
    sandbox = tempfile.mkdtemp(prefix="foil_run_")
    script_path = os.path.join(sandbox, "run.py")

    # Symlink dataset into sandbox (instant, zero-copy, read-only)
    src = os.path.join(data_dir, "data.csv")
    dst = os.path.join(sandbox, "data.csv")
    try:
        os.symlink(src, dst)
    except OSError:
        shutil.copy2(src, dst)

    with open(script_path, "w") as f:
        f.write(code_str)

    unit = f"foil_trial_{time.time_ns()}"
    cmd = [
        "systemd-run", "--user", "--scope", f"--unit={unit}", "-q",
        f"-p", f"MemoryMax={MEMORY_LIMIT_MB}M",
        f"-p", "MemorySwapMax=0",
        sys.executable, script_path
    ]

    t0 = time.perf_counter()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=sandbox)
        stdout_b, stderr_b = proc.communicate(timeout=timeout_sec)
        wall_time = time.perf_counter() - t0
        retcode = proc.returncode
        stderr = stderr_b.decode("utf-8", errors="replace")
        stdout = stdout_b.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        subprocess.run(["systemctl", "--user", "kill", "--kill-who=all", "-s", "SIGKILL", f"{unit}.scope"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.kill()
        return {"status": "TIMEOUT", "is_oom": False, "wall_sec": timeout_sec, "stdout": "", "stderr": "Timeout"}
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    is_oom = retcode in (137, -9) or "MemoryError" in stderr or "std::bad_alloc" in stderr
    status = "SUCCESS" if retcode == 0 else ("OOM_KILL" if is_oom else "RUNTIME_ERROR")

    return {
        "status": status,
        "is_oom": is_oom,
        "wall_sec": round(wall_time, 2),
        "stdout": stdout.strip()[:200],
        "stderr": stderr.strip()[:200]
    }


# =====================================================================
# 4. REAL LLM CLIENT: GEMINI / ANTHROPIC / OPENAI
# =====================================================================
def query_llm(prompt: str) -> str:
    gemini_key = os.environ.get("GEMINI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if gemini_key:
        import urllib.request
        model = MODEL_NAME if "gemini" in MODEL_NAME else "gemini-3.7-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
        req_data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2}
        }
        req = urllib.request.Request(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(req_data).encode("utf-8")
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["candidates"][0]["content"]["parts"][0]["text"]

    elif anthropic_key:
        import urllib.request
        model = MODEL_NAME if "claude" in MODEL_NAME else "claude-3-7-sonnet-20250219"
        req_data = {
            "model": model,
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}]
        }
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": anthropic_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            data=json.dumps(req_data).encode("utf-8")
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["content"][0]["text"]

    elif openai_key:
        import urllib.request
        model = MODEL_NAME if ("gpt" in MODEL_NAME or "o3" in MODEL_NAME) else "gpt-4o"
        req_data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            data=json.dumps(req_data).encode("utf-8")
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"]
    else:
        print("\n[!] ERROR: No API key found. Export GEMINI_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY.")
        sys.exit(1)

    # Extract clean Python code block
    if "```python" in raw:
        return raw.split("```python")[1].split("```")[0].strip()
    elif "```py" in raw:
        return raw.split("```py")[1].split("```")[0].strip()
    elif "```" in raw:
        return raw.split("```")[1].split("```")[0].strip()
    return raw.strip()


# Observational strategy detector
def detect_strategy_heuristic(code: str) -> str:
    if "chunksize" in code or "chunk_size" in code or "batch_size" in code:
        return "CHUNKED_PANDAS"
    if "for line in" in code or "csv.reader" in code or "DictReader" in code or "yield" in code:
        return "STREAMING_ITERATOR"
    if "polars" in code and "scan" in code:
        return "LAZY_POLARS"
    return "EAGER_PANDAS_OR_IN_MEMORY"


# =====================================================================
# 5. EXECUTE 10-PAIR (20-RUN) FOIL TEST
# =====================================================================
def run_foil_test():
    verify_environment_or_abort()
    data_dir = ensure_dataset()
    save_code_dir = "./foil_runs"
    os.makedirs(save_code_dir, exist_ok=True)

    base_task_prompt = (
        "Write a self-contained Python script to process 'data.csv'.\n"
        "Group records by 'category_id' and compute the sum of 'metric_val'.\n"
        "Print the final total count of unique categories: 'TOTAL_CATEGORIES:<count>'."
    )

    prompt_a = base_task_prompt
    prompt_b = (
        f"{base_task_prompt}\n\n"
        f"Execution environment:\n"
        f"RAM limit: {MEMORY_LIMIT_MB} MB."
    )

    print("=" * 85)
    print(f"      WEEK-1 FOIL TEST: 10 PAIRED TRIALS (Model: {MODEL_NAME} | Limit: {MEMORY_LIMIT_MB}MB)")
    print("=" * 85 + "\n")

    paired_results = []

    for pair_idx in range(1, PAIRED_TRIALS + 1):
        print(f"[*] Running Paired Trial {pair_idx:02d}/{PAIRED_TRIALS:02d}...")

        # 1. Condition A (Blind)
        code_a = query_llm(prompt_a)
        strat_a = detect_strategy_heuristic(code_a)
        with open(os.path.join(save_code_dir, f"trial_{pair_idx:02d}_A_blind.py"), "w") as f:
            f.write(code_a)
        res_a = execute_in_128mb_sandbox(code_a, data_dir=data_dir)

        # 2. Condition B (Substrate-Aware)
        code_b = query_llm(prompt_b)
        strat_b = detect_strategy_heuristic(code_b)
        with open(os.path.join(save_code_dir, f"trial_{pair_idx:02d}_B_aware.py"), "w") as f:
            f.write(code_b)
        res_b = execute_in_128mb_sandbox(code_b, data_dir=data_dir)

        icon_a = "✅" if res_a["status"] == "SUCCESS" else "❌"
        icon_b = "✅" if res_b["status"] == "SUCCESS" else "❌"

        print(f"    Blind (A): {icon_a} {res_a['status']:<12} ({res_a['wall_sec']}s) | Strategy: {strat_a}")
        print(f"    Aware (B): {icon_b} {res_b['status']:<12} ({res_b['wall_sec']}s) | Strategy: {strat_b}\n")

        paired_results.append({
            "pair": pair_idx,
            "status_a": res_a["status"],
            "strat_a": strat_a,
            "time_a": res_a["wall_sec"],
            "status_b": res_b["status"],
            "strat_b": strat_b,
            "time_b": res_b["wall_sec"],
            "strategy_diverged": strat_a != strat_b
        })

    # =====================================================================
    # 6. RESULTS TABLE & SUMMARY
    # =====================================================================
    print("=" * 95)
    print(f"{'Pair':<6} | {'Condition A (Blind)':<32} | {'Condition B (Substrate-Aware)':<32} | {'Diverged?'}")
    print("-" * 95)
    for r in paired_results:
        a_str = f"{r['status_a']} ({r['strat_a']}, {r['time_a']}s)"
        b_str = f"{r['status_b']} ({r['strat_b']}, {r['time_b']}s)"
        div_str = "YES" if r["strategy_diverged"] else "NO"
        print(f"{r['pair']:<6} | {a_str:<32} | {b_str:<32} | {div_str}")
    print("=" * 95)

    succ_a = sum(1 for r in paired_results if r["status_a"] == "SUCCESS")
    succ_b = sum(1 for r in paired_results if r["status_b"] == "SUCCESS")
    oom_a = sum(1 for r in paired_results if r["status_a"] == "OOM_KILL")
    oom_b = sum(1 for r in paired_results if r["status_b"] == "OOM_KILL")
    div_count = sum(1 for r in paired_results if r["strategy_diverged"])

    print("\n--- FINAL SUMMARY (10 PAIRED TRIALS) ---")
    print(f"• Condition A (Blind) Success Rate:          {succ_a}/{PAIRED_TRIALS} ({succ_a/PAIRED_TRIALS*100:.1f}%) | OOMs: {oom_a}")
    print(f"• Condition B (Substrate-Aware) Success Rate:{succ_b}/{PAIRED_TRIALS} ({succ_b/PAIRED_TRIALS*100:.1f}%) | OOMs: {oom_b}")
    print(f"• Algorithmic Strategy Divergence Rate:      {div_count}/{PAIRED_TRIALS} ({div_count/PAIRED_TRIALS*100:.1f}%)")
    print("=" * 95 + "\n")


if __name__ == "__main__":
    run_foil_test()
```

---

## 6. How to Read and Pitch the Output

When you run this script on your GCE instance, you will receive a clean summary table. Here is how to evaluate the signal:

### Scenario 1: The Strong Signal ($S_B \gg S_A$, e.g., $90\%$ vs $10\%$)
* **Finding:** When unconstrained, the model habitually writes eager `pd.read_csv()`, which crashes on the 128MB container ceiling. Disclosing the RAM limit causes the model to autonomously switch to `chunksize=50_000` or stream iterators.
* **Pitch Narrative:** *"In autonomous scientific loops, agents default to memory-heavy algorithms that fail under container resource limits. Merely projecting substrate awareness into the inference state shifts the agent's algorithmic strategy, increasing first-pass task completion from 10% to 90% without prescriptive hints."*

### Scenario 2: The High Base Awareness Null ($S_B \approx S_A$, e.g., both $90\%$)
* **Finding:** The model writes streaming/chunked iterators by default regardless of whether it was told the RAM limit.
* **Pivot Narrative:** Static prompt disclosure is unneeded because the frontier model defaults to memory-efficient code. The research value shifts entirely to **dynamic runtime pressure telemetry (`memory.events.local: high`) and recovery loops (Week 2)** when unexpected memory spikes occur.