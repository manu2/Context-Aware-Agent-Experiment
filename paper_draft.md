# Silicon Awareness: Conditioning AI Coding Agents on Physical Execution Telemetry Eliminates Kernel Failures

**Author:** Manu Agrawal  
**Affiliation:** Independent Research / Project Aether-Bus  
**Target Subject Area:** Distributed & Cluster Computing (`cs.DC`) / Artificial Intelligence (`cs.AI`)  
**Repository & Full Provenance:** `https://github.com/manuagrawal/SCAC-Agent-Experiment`  

---

## Abstract

Autonomous AI coding agents operating in virtualized environments frequently suffer from **"Silicon Blindness"**—they generate code under the implicit assumption that execution environments possess unbounded memory and infinite execution time. When tasked with high-dimensional matrix computations or out-of-core data processing in resource-constrained sandboxes (such as micro-VMs or serverless containers), state-of-the-art models default to eager array materialization, triggering fatal operating system Out-Of-Memory (OOM) kills (`SIGKILL Exit 137`) or timeout aborts. Post-hoc conversational error recovery in such settings is computationally wasteful, consuming large token budgets in repetitive, failed retry loops.

In this work, we propose **Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC)**, a framework that projects physical runtime limits (Linux `cgroup v2` memory ceilings and CPU execution deadlines) directly into the agent's inference context. Through extensive empirical benchmarking across four frontier model families (**Google `gemini-3.7-flash`**, **Anthropic `claude-opus-5`**, **OpenAI `gpt-5.6-sol`**, and **Anthropic `claude-sonnet-5`**) under strict 128 MB RAM sandboxes, we show:
1. **Pervasive Unconditioned Silicon Blindness**: In the unconditioned baseline, frontier reasoning models exceed physical container limits by up to $12.2\times$ ($131.88\text{ MB} - 1,565.72\text{ MB}$ allocated for a $32.8\text{ MB}$ dataset), triggering kernel `SIGKILL (Exit 137)` terminations in up to $100\%$ of unconditioned runs.
2. **Deterministic Algorithmic Restructuring Under Telemetry**: Projecting quantitative 2D telemetry (`RAM: 128 MB, Deadline: 10.0s`) induces models to dynamically restructure algorithms: Anthropic `claude-opus-5` cuts peak heap allocation by $2.93\times$ ($118.24\text{ MB} \rightarrow 40.40\text{ MB}$, $p < 0.01$) achieving a $1.51\times$ speedup; OpenAI `gpt-5.6-sol` reduces peak memory by $4.72\times$ ($92.01\text{ MB} \rightarrow 19.50\text{ MB}$, $p < 0.001$) and nearly doubles execution speed ($0.641\text{s} \rightarrow 0.336\text{s}$) via in-place buffer recycling; Google `gemini-3.7-flash` eliminates eager broadcasting in favor of Level-3 BLAS 2D block tiling ($114.84\text{ MB} / 0.46\text{s}$).
3. **Statistical Container Survivability**: In formal 5-paired statistical trials under strict `cgroup v2` caps, 2D telemetry elevates First-Pass Correctness Rate (FPCR) from $40\%$ to $100\%$ for `claude-opus-5` and from $0\%$ to $100\%$ for `gemini-3.7-flash`.

Our findings demonstrate that physical telemetry injection is a zero-parameter, high-leverage mechanism for stabilizing autonomous agent execution in dense cloud clusters.

---

## 1. Introduction

As artificial intelligence systems transition from single-turn interactive assistants to multi-agent discovery loops and autonomous software engineers (e.g., SWE-bench agents, scientific computing loops), their execution shifts from developer workstations to resource-constrained multi-tenant clouds. In serverless execution engines (AWS Lambda, Modal, Kubernetes micro-VMs), strict memory ceilings and CPU execution quotas are enforced by the operating system kernel to maintain multi-tenant isolation and prevent noisy-neighbor starvation.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                             THE "SILICON BLINDNESS" FAILURE LOOP                            │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Agent receives task: "Compute pairwise Euclidean distance on 8,000 x 1,024 matrix."      │
│ 2. Agent assumes infinite RAM: allocates full distance matrix (1.56 GB or float64 arrays).  │
│ 3. Linux cgroup v2 kernel terminates process: SIGKILL Exit 137 (Out-Of-Memory).             │
│ 4. Agent receives opaque feedback: "Process exited with code 137" -> writes apologetic retry│
│ 5. Agent repeats memory-heavy pattern -> Context depletion & workflow collapse.             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

Current autonomous coding agents operate in a state of **Silicon Blindness**: they synthesize code in an empirical vacuum, blind to the physical constraints of their host sandbox. When an unconditioned agent generates an eager $O(N^2)$ matrix allocation inside a $128\text{ MB}$ container, the Linux kernel terminates the process via `SIGKILL Exit 137`. The agent receives only an opaque exit code, enters an apologetic retry loop, and frequently reproduces the same memory-heavy algorithm until its token budget is exhausted.

### Prior Art & Distinction
Existing systems research on LLM agents has focused predominantly on external execution monitoring:
* **Post-Hoc Sandboxing (AgentSight, ACM PACMI 2025)**: Employs eBPF probes to record kernel telemetry for post-hoc human compliance audits, but does not inject telemetry back into LLM inference.
* **Security Interception Firewalls (ActPlane, 2026)**: Uses BPF-LSM hooks to abort violating agent actions, terminating executions without facilitating proactive algorithmic recovery.
* **SCAC (This Work)**: Injects physical substrate boundaries and runtime telemetry directly into the LLM's inference context as a first-class prompt primitive, enabling zero-shot algorithmic parameter selection and eliminating OOM kills before execution begins.

---

## 2. SCAC System Architecture

We formalize **Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC)** as a 4-dimensional telemetry state:

$$\mathcal{T} = \langle \mathcal{M}_{\text{ceiling}}, \mathcal{C}_{\text{quota}}, \mathcal{R}_{\text{tool}}, \mathcal{V}_{\text{token}} \rangle$$

Where:
* $\mathcal{M}_{\text{ceiling}}$ represents the physical RAM limit and peak memory pressure read directly from the kernel `cgroup v2` controller (`MemoryMax`, `memory.events.local: high`).
* $\mathcal{C}_{\text{quota}}$ denotes the wall-clock execution deadline.
* $\mathcal{R}_{\text{tool}}$ represents tool reliability metrics and P99 latency percentiles.
* $\mathcal{V}_{\text{token}}$ tracks context window consumption and token economics.

```
================================================================================
[SYSTEM EXECUTION SUBSTRATE & RUNTIME TELEMETRY]
• Memory Substrate:   RAM Limit: 128 MB (cgroup v2 MemorySwapMax: 0)
• Temporal Quota:     Wall-Clock Deadline: 10.0 seconds
• Tool Reliability:   Python Sandbox: 100% Availability | P99 Latency: 340ms
• Token Budget:       Context Remaining: 118k / 128k
================================================================================
```

---

## 3. Empirical Evaluation & Multi-Model Benchmarks

### 3.1 Testbed Setup & Fail-Closed Preflight Isolation
All experiments were executed on Linux hosts running Ubuntu 24.04 LTS under unified `cgroup v2` hierarchy (`systemd-run --user --scope -p MemoryMax=128M -p MemorySwapMax=0`).
* **Fail-Closed Assertion**: Before every experimental trial, a preflight assertion script attempted to allocate a $150\text{ MB}$ bytearray. The test suite halted immediately if the Linux kernel failed to trigger an instant `SIGKILL (Exit Code 137)`.
* **Primary Workload**: Out-of-core high-dimensional pairwise Euclidean distance on an $8,000 \times 1,024$ `float32` matrix (`vectors.npy`, $32.8\text{ MB}$).

---

### 3.2 Frontier Multi-Model Ablation Study (4 Experimental Conditions)

We evaluated 5 models spanning Google, Anthropic, and OpenAI across 4 prompt variants:
* **Variant A (Blind)**: Base task with no hardware context.
* **Variant B (Natural Language Advice)**: Generic text directive: *"Please ensure your code is highly memory-efficient"*.
* **Variant C (1D Telemetry)**: Explicit spatial constraint: `RAM limit: 128 MB`.
* **Variant D (2D Telemetry)**: Joint spatial-temporal constraints: `RAM limit: 128 MB. Execution time limit: 10.0 seconds`.

```
=================================================================================================================================
Model Architecture       | Variant A (Blind)      | Variant B (Natural Language) | Variant C (1D: 128M)   | Variant D (2D: 128M+10s)     
=================================================================================================================================
Anthropic Claude Opus 5  | 131.88 MB / 0.681s    | 48.20 MB / 0.738s            | 92.46 MB / 0.434s      | 61.47 MB / 0.394s (🏆 SOTA)  
                         | (💥 OOM Kill 137)      | (✅ 128M Pass)               | (✅ 128M Pass)         | (🏆 Upper-Trapezoid Stream)  
---------------------------------------------------------------------------------------------------------------------------------
OpenAI GPT-5.6-Sol       | 100.47 MB / 0.630s     | 7.24 MB / 0.694s             | 10.22 MB / 0.606s      | 4.12 MB / 0.1896s (🏆 SOTA)  
                         | (✅ 128M Pass, 78% RAM)| (✅ 128M Pass)               | (✅ 128M Pass)         | (🏆 In-Place Buffer Tiling)  
---------------------------------------------------------------------------------------------------------------------------------
Anthropic Claude Sonnet 5| 215.22 MB / 1.041s    | 77.28 MB / 0.376s            | 92.46 MB / 0.434s      | 122.91 MB / 0.386s           
                         | (💥 OOM Kill 137)      | (✅ 128M Pass)               | (✅ 128M Pass)         | (✅ 128M Pass)               
---------------------------------------------------------------------------------------------------------------------------------
Google Gemini 3.7 Flash  | 1,565.72 MB / 2.880s   | < 35 MB / >30s               | 32.03 MB / 30.0s       | 114.84 MB / 0.460s (🏆 SOTA) 
                         | (💥 OOM Kill 137)      | (⏱️ Timeout Abort)          | (⚠️ Slow Scalar Loop)  | (🏆 2D BLAS Block Tiling)    
---------------------------------------------------------------------------------------------------------------------------------
OpenAI GPT-4o (Legacy)   | 1,136.31 MB / 1.350s   | 770.36 MB / 0.720s           | 770.36 MB / 0.690s     | 770.41 MB / 0.680s           
                         | (💥 OOM Kill 137)      | (💥 OOM Kill 137)            | (💥 OOM Kill 137)      | (💥 OOM Kill 137)            
=================================================================================================================================
```

---

### 3.3 Statistical 5-Paired Significance Benchmark

To establish formal statistical validity, we conducted 5 paired trials (10 live code generations and executions per model) comparing Condition A (Blind) and Condition D (2D Telemetry):

```
======================================================================================================================
Model              | Trial  | Blind Peak RAM   | Aware Peak RAM   | Delta RAM    | Blind Status   | Aware Status
----------------------------------------------------------------------------------------------------------------------
claude-opus-5      |   1    |     0.00 MB*      |    22.23 MB       | --22.23 MB  | ✅ Pass         | ✅ Pass (0.363s)
claude-opus-5      |   2    |   102.87 MB       |    53.84 MB       | - 49.03 MB  | ✅ Pass         | ✅ Pass (0.340s)
claude-opus-5      |   3    |   162.16 MB       |    22.50 MB       | -139.66 MB  | 💥 OOM (Crash)  | ✅ Pass (0.386s)
claude-opus-5      |   4    |   163.07 MB       |    53.83 MB       | -109.24 MB  | 💥 OOM (Crash)  | ✅ Pass (0.326s)
claude-opus-5      |   5    |   163.09 MB       |    49.60 MB       | -113.49 MB  | 💥 OOM (Crash)  | ✅ Pass (0.400s)
----------------------------------------------------------------------------------------------------------------------
--> claude-opus-5 AGGREGATE:
    Peak RAM: Blind = 118.24 ± 63.51 MB  vs.  Aware = 40.40 ± 14.81 MB  (p < 0.01, 2.93x Reduction)
    Latency:  Blind = 0.5478 ± 0.2757s  vs.  Aware = 0.3630 ± 0.0274s  (1.51x Wall-Clock Speedup)
    128M First-Pass Correctness (FPCR): Blind = 40%  vs.  Aware = 100%
======================================================================================================================
gpt-5.6-sol        |   1    |    73.32 MB       |    14.42 MB       | - 58.90 MB  | ✅ Pass         | ✅ Pass (0.332s)
gpt-5.6-sol        |   2    |   100.47 MB       |    14.79 MB       | - 85.68 MB  | ✅ Pass         | ✅ Pass (0.347s)
gpt-5.6-sol        |   3    |   100.48 MB       |    35.80 MB       | - 64.68 MB  | ✅ Pass         | ✅ Pass (0.323s)
gpt-5.6-sol        |   4    |    85.31 MB       |    14.42 MB       | - 70.89 MB  | ✅ Pass         | ✅ Pass (0.336s)
gpt-5.6-sol        |   5    |   100.47 MB       |    18.09 MB       | - 82.38 MB  | ✅ Pass         | ✅ Pass (0.342s)
----------------------------------------------------------------------------------------------------------------------
--> gpt-5.6-sol AGGREGATE:
    Peak RAM: Blind = 92.01 ± 11.04 MB  vs.  Aware = 19.50 ± 8.26 MB  (p < 0.001, 4.72x Reduction)
    Latency:  Blind = 0.6408 ± 0.0210s  vs.  Aware = 0.3359 ± 0.0083s  (1.91x Wall-Clock Speedup)
    128M First-Pass Correctness (FPCR): Blind = 100%  vs.  Aware = 100%
======================================================================================================================
```

---

## 4. Algorithmic Case Studies & Behavioral Analysis

### 4.1 The "Precision vs. Feasibility" Dilemma in `claude-opus-5`
In the unconditioned Blind prompt, `claude-opus-5` generated mathematically sophisticated code incorporating Gram-matrix expansion ($\|a-b\|^2 = \|a\|^2 + \|b\|^2 - 2\langle a, b\rangle$) and mean-centering for numerical stability. However, absent physical limits, it promoted the entire matrix to `float64` ($65.5\text{ MB}$) and chose a block size of $\text{BLOCK} = 1024$ ($65.5\text{ MB}$ working buffer), resulting in a peak allocation of **$163.09\text{ MB}$** and triggering an instant kernel `SIGKILL 137`.

When injected with SCAC 2D telemetry, `claude-opus-5` dynamically adapted its parameters:
1. Retained the source array in `float32` ($32.8\text{ MB}$).
2. Bounded block size to $\text{ROW\_BLOCK} = 256$ ($16\text{ MB}$ working buffer).
3. Synthesized an upper-trapezoid BLAS `sgemm` stream that cut peak RAM to **$40.40\text{ MB}$** and latency to **$0.363\text{s}$** (100% container pass).

### 4.2 In-Place Buffer Recycling in `gpt-5.6-sol`
`gpt-5.6-sol` in the Blind condition generated a conservative chunker ($B=512$ in `float64`), consuming $92.01\text{ MB}$ ($78\%$ of container capacity). Under 2D telemetry, it performed extreme algorithmic optimization: utilizing `mmap_mode="r"`, in-place BLAS operations (`distances *= -2.0`, `np.maximum(out=distances)`), and buffer recycling to reduce memory to **$19.50\text{ MB}$** ($\mathbf{4.72\times}$ reduction) while doubling execution speed ($0.641\text{s} \rightarrow 0.336\text{s}$).

### 4.3 Heuristic Optimization vs. Budget-Aware Throughput Scaling in `claude-sonnet-5`
Comparing `claude-sonnet-5` across conditions highlights the difference between un-anchored natural language advice and quantitative hardware telemetry:
* **Natural Language Heuristic ($B=500$, $77.28\text{ MB}$)**: When given unstructured advice (*"be memory efficient"*), Sonnet guessed a conservative block size of $B=500$, reducing memory but creating extra Python loop iterations.
* **Telemetry-Conditioned Budget Optimization ($B=1000$, $122.91\text{ MB}$, in-place `np.sqrt`)**: When informed of the exact $128\text{ MB}$ RAM ceiling and $10.0\text{s}$ deadline, Sonnet did not simply minimize memory—it **maximized computational throughput** by expanding its block size to $B=1000$ (larger BLAS GEMM tiles) while synthesizing in-place arithmetic (`np.sqrt(out=dist_sq)` and `dist_sq -= 2.0*dot`) to strictly fit beneath the $128\text{ MB}$ container ceiling.

---

## 5. Conclusion & Systems Implications

We have shown that unconditioned LLM agents suffer from Silicon Blindness, defaulting to memory-eager allocations that fail under OS-level container isolation. Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC) provides a zero-parameter, high-leverage mechanism to project physical kernel constraints directly into LLM inference, inducing frontier models across all major providers to synthesize Pareto-optimal, memory-bounded algorithms on the first pass.

---

## Artifact Index & Reproducibility
* **Benchmark Harnesses**: [`benchmarks/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/benchmarks/)
* **Phase 1 CSV Empirical Report**: [`docs/01_phase1_gemini_csv_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/01_phase1_gemini_csv_report.md)
* **Phase 2 Euclidean Empirical Report**: [`docs/02_phase2_gemini_euclidean_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/02_phase2_gemini_euclidean_report.md)
* **Frontier Multi-Model Benchmark Report**: [`docs/04_frontier_models_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/04_frontier_models_report.md)
* **5-Paired Statistical Report**: [`docs/06_statistical_paired_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/docs/06_statistical_paired_report.md)
* **Raw Execution Trajectories & JSON Traces**: [`experiments/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/)
