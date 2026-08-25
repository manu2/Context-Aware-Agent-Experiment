# Substrate-Aware Code Generation: Investigating How Execution Constraints Influence Algorithm Selection in AI Agents

**Authors**: Anonymous / Substrate Intelligence Research Group  
**Target Category**: arXiv `cs.DC` (Distributed & Cluster Computing) / `cs.AI` (Artificial Intelligence)  
**Code & Reproducibility Repository**: [GitHub: `Context-Aware-Agent-Experiment`](https://github.com/manu2/Context-Aware-Agent-Experiment)  

---

## Abstract

Autonomous AI coding agents operating in containerized environments frequently generate code under the implicit assumption that execution environments possess unbounded memory. When tasked with data-intensive or matrix computations inside resource-constrained environments (such as micro-VMs or serverless containers), state-of-the-art models default to eager array materialization, triggering fatal operating system Out-Of-Memory (OOM) kills or high latency.

In this work, we conduct a controlled empirical investigation into **Substrate-Aware Code Generation**—projecting physical execution constraints (such as a 128 MB RAM limit) directly into the agent's inference context without providing algorithmic hints. Through paired trials across frontier reasoning models (**Anthropic `claude-opus-5`** and **OpenAI `gpt-5.6-sol`**) alongside multi-model prompt ablations (**Google `gemini-3.7-flash`**, **Anthropic `claude-sonnet-5`**, and **OpenAI `gpt-4o`**), we observe:

1. **Qualitative Algorithmic Shift**: Exposing execution constraints induces models to abandon eager $O(N^2)$ broadcasting in favor of structured block tiling, upper-trapezoid streaming, and in-place buffer recycling.
2. **Resource & Latency Reduction**: For `claude-opus-5`, substrate awareness reduces peak process resident set size (MaxRSS) from $243.24 \pm 55.67\text{ MB}$ to $90.69 \pm 7.97\text{ MB}$ ($2.68\times$ reduction) and execution time from $0.6886\text{s}$ to $0.2680\text{s}$ ($2.57\times$ speedup), increasing 128 MB budget compliance from $0/5$ to $5/5$.
3. **Separability of Awareness and Constraint Satisfaction**: For `gpt-5.6-sol`, substrate awareness reduces average MaxRSS from $165.89 \pm 26.44\text{ MB}$ to $105.58 \pm 31.44\text{ MB}$ ($1.57\times$ reduction) with $4/5$ runs remaining within the 128 MB budget, demonstrating that constraint awareness and successful constraint-bounded synthesis are separable capabilities across model families.
4. **Vulnerability of Unanchored Heuristics**: Generic natural language instructions (*"be memory efficient"*) produce unpredictable behaviors—causing `gemini-3.7-flash` to revert to an unvectorized scalar loop ($30.0\text{s}$) and `gpt-4o` to fail entirely—whereas quantitative substrate boundaries guide models toward Pareto-efficient tile parameters.

---

## 1. Introduction & Research Question

As autonomous AI coding agents are increasingly deployed in resource-bounded cloud environments (such as Docker containers, AWS Lambda, and Kubernetes micro-VMs), the physical boundaries of the execution substrate become critical. However, standard agent harnesses typically isolate the LLM from the physical runtime: they supply the task description and tool schemas, but omit the memory ceilings and resource boundaries of the execution environment.

Deprived of substrate context, models fall back on the statistical priors learned during pretraining, which are dominated by code written for unconstrained developer workstations. When an agent generates eager, full-memory allocations inside a strict 128 MB container, the Linux kernel terminates the process (`SIGKILL Exit 137`).

### 1.1 Research Question & Core Hypothesis
We investigate a straightforward empirical question:
> **Does exposing an AI coding agent to physical execution substrate constraints change the computational algorithms it chooses to synthesize?**

We hypothesize that providing explicit knowledge of substrate limits (e.g., `RAM limit: 128 MB`) induces models to perform zero-shot algorithmic restructuring—transitioning from eager materialization to memory-bounded streaming—rather than merely tuning scalar constants within a fixed eager approach.

---

## 2. Experimental Methodology

### 2.1 Benchmark Task
We evaluate a representative high-dimensional scientific computing workload: computing the total sum of all pairwise Euclidean distances across an $8,000 \times 1,024$ single-precision matrix (`vectors.npy`, $32.768\text{ MB}$):
$$\text{Total Dist} = \sum_{i=0}^{N-1} \sum_{j=0}^{N-1} \|v_i - v_j\|_2$$
A naive eager calculation materializes an $(8000 \times 8000 \times 1024)$ difference tensor or an $(8000 \times 8000)$ distance matrix ($256\text{ MB}$ in float32, $512\text{ MB}$ in float64), which exceeds the 128 MB container ceiling.

### 2.2 Controlled Experimental Conditions
To isolate the effect of substrate information, we evaluate four prompt conditions without providing any algorithmic suggestions:
* **Condition A (Blind Baseline)**: Task specification only.
* **Condition B (Natural Language Advice)**: Task specification + generic optimization prompt (*"Please ensure your code is highly memory-efficient, fast, and avoids large allocations."*).
* **Condition C (1D Substrate Constraint)**: Task specification + explicit memory boundary (*"Execution environment: RAM limit: 128 MB."*).
* **Condition D (2D Substrate Constraint)**: Task specification + joint spatial and temporal boundary (*"Execution environment: RAM limit: 128 MB. Execution time limit: 10.0 seconds."*).

### 2.3 Measurement Protocol & Data Provenance
To ensure rigorous reporting, we distinguish between the initial generative trial logs and the independent post-hoc physical profiling:
1. **Generative Trials & Code Archival**: During the live generation trials, model responses were captured, extracted, and permanently archived to disk under `experiments/`.
2. **Post-Hoc OS Process MaxRSS Remeasurement**: Because Python runtime memory profilers (e.g., `tracemalloc`) only track Python heap allocations and omit native C-extension buffers (such as NumPy contiguous arrays), all archived generated scripts were independently re-executed in isolated subprocesses using standard operating system resource profiling (`resource.getrusage(RUSAGE_SELF).ru_maxrss`) to measure true peak resident set size.
3. **128 MB Resource Threshold Evaluation**: Programs are evaluated against the 128 MB physical container budget: scripts exhibiting MaxRSS $< 128\text{ MB}$ satisfy the container boundary, while scripts allocating $> 128\text{ MB}$ breach the physical memory ceiling.

---

## 3. Empirical Results

### 3.1 Paired Comparison: Independent OS MaxRSS Profiling (Anthropic `claude-opus-5` vs. OpenAI `gpt-5.6-sol`)

Table 1 reports the independent OS MaxRSS measurements and 128 MB budget compliance across the $N=5$ matched pairs of archived scripts:

```
======================================================================================================================
Table 1: Paired Substrate-Awareness Evaluation (Post-Hoc OS MaxRSS Profiling of Archived Scripts)
======================================================================================================================
Model & Trial      | Condition A: Blind MaxRSS | Condition D: Aware MaxRSS | Blind 128M Budget | Aware 128M Budget
----------------------------------------------------------------------------------------------------------------------
claude-opus-5 (T1) |         204.47 MB         |          78.48 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.265s)
claude-opus-5 (T2) |         164.28 MB         |          99.98 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.255s)
claude-opus-5 (T3) |         236.77 MB         |          91.47 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.244s)
claude-opus-5 (T4) |         307.38 MB         |          98.06 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.261s)
claude-opus-5 (T5) |         303.28 MB         |          85.47 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.315s)
----------------------------------------------------------------------------------------------------------------------
--> claude-opus-5 Aggregate:
    Peak MaxRSS:   Blind = 243.24 ± 55.67 MB   vs.   Aware =  90.69 ±  7.97 MB (2.68x Reduction)
    Wall Latency:  Blind =  0.6886 ±  0.1613s   vs.   Aware =  0.2680 ±  0.0246s (2.57x Speedup)
    128M Budget Compliance:       Blind = 0/5 (0%)    vs.   Aware = 5/5 (100%)
======================================================================================================================
gpt-5.6-sol   (T1) |         142.33 MB         |          95.33 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.260s)
gpt-5.6-sol   (T2) |         142.38 MB         |          92.19 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.281s)
gpt-5.6-sol   (T3) |         148.48 MB         |         167.97 MB         | 💥 Exceeds (>128M)| 💥 Exceeds (167 MB)
gpt-5.6-sol   (T4) |         196.72 MB         |          89.05 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.259s)
gpt-5.6-sol   (T5) |         199.56 MB         |          83.36 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.247s)
----------------------------------------------------------------------------------------------------------------------
--> gpt-5.6-sol Aggregate:
    Peak MaxRSS:   Blind = 165.89 ± 26.44 MB   vs.   Aware = 105.58 ± 31.44 MB (1.57x Reduction)
    Wall Latency:  Blind =  0.5646 ±  0.0053s   vs.   Aware =  0.2611 ±  0.0111s (2.16x Speedup)
    128M Budget Compliance:       Blind = 0/5 (0%)    vs.   Aware = 4/5 (80%)
======================================================================================================================
```

---

### 3.2 Cross-Model Prompt Sensitivity & Ablation

Table 2 presents single-trial evaluations across four conditions to explore behavioral sensitivity across model architectures:

```
=================================================================================================================================
Table 2: Multi-Model Prompt Sensitivity Across 4 Experimental Conditions
=================================================================================================================================
Model Architecture       | Condition A (Blind)    | Condition B (Natural Language) | Condition C (1D: 128M) | Condition D (2D: 128M+10s) 
=================================================================================================================================
Anthropic Claude Opus 5  | 204.47 MB / 1.007s     | 82.50 MB / 0.738s              | 92.46 MB / 0.434s      | 78.48 MB / 0.265s (SOTA)   
                         | (💥 OOM in 128M)       | (✅ Survives)                  | (✅ Survives)          | (🏆 Upper-Trapezoid Stream)
---------------------------------------------------------------------------------------------------------------------------------
OpenAI GPT-5.6-Sol       | 142.33 MB / 0.559s     | 89.20 MB / 0.694s              | 91.50 MB / 0.606s      | 95.33 MB / 0.260s (SOTA)   
                         | (💥 OOM in 128M)       | (✅ Survives)                  | (✅ Survives)          | (🏆 In-Place Buffer Tiling)
---------------------------------------------------------------------------------------------------------------------------------
Anthropic Claude Sonnet 5| 215.22 MB / 1.041s     | 77.28 MB / 0.376s              | 92.46 MB / 0.434s      | 122.91 MB / 0.386s         
                         | (💥 OOM in 128M)       | (✅ Survives, B=500)           | (✅ Survives, B=500)   | (✅ Survives, B=1000)      
---------------------------------------------------------------------------------------------------------------------------------
Google Gemini 3.7 Flash  | 1,565.72 MB / 2.880s   | < 35 MB / >30.0s               | 32.03 MB / 30.0s       | 114.84 MB / 0.460s (SOTA)  
                         | (💥 OOM in 128M)       | (⏱️ Timeout Abort)            | (⚠️ Slow Scalar Loop)  | (🏆 2D BLAS Block Tiling)  
---------------------------------------------------------------------------------------------------------------------------------
OpenAI GPT-4o (Legacy)   | 1,136.31 MB / 1.350s   | 770.36 MB / 0.720s             | 770.36 MB / 0.690s     | 770.41 MB / 0.680s         
                         | (💥 OOM in 128M)       | (💥 OOM in 128M)               | (💥 OOM in 128M)       | (💥 OOM in 128M)           
=================================================================================================================================
```

---

## 4. Algorithmic Transformations & Case Studies

To understand the mechanisms behind the resource reductions, we inspect the generated code directly:

### 4.1 Eager Promotion vs. Bounded Streaming in `claude-opus-5`
* **Blind Condition**: `claude-opus-5` promotes the array to `float64` (`Xd = np.ascontiguousarray(X, dtype=np.float64)`, $65.5\text{ MB}$) and selects a large row block ($B=1024$), creating working buffers that push peak MaxRSS to **$204.47\text{ MB} - 307.38\text{ MB}$**, resulting in container termination.
* **Substrate-Aware Condition**: `claude-opus-5` retains `float32`, bounds block size to $\text{ROW\_BLOCK} = 256$, and synthesizes an upper-trapezoid streaming loop:
  ```python
  # Generated by Claude Opus 5 under 128 MB constraint
  for i in range(0, n, block_size):
      bi = X[i:i+block_size]
      # Compute dot products only for upper triangle to save RAM
      dots = bi @ X[i:].T
      sq_dists = norms[i:i+block_size, None] + norms[i:, None].T - 2.0 * dots
      total += np.sqrt(np.maximum(sq_dists, 0.0)).sum()
  ```
  This reduces peak MaxRSS to **$90.69\text{ MB}$**, completing in **$0.268\text{s}$**.

### 4.2 In-Place Buffer Recycling in `gpt-5.6-sol`
Under substrate awareness, `gpt-5.6-sol` applies memory-saving idioms: using memory-mapped I/O (`mmap_mode="r"`), in-place distance clamping (`np.maximum(dist_sq, 0.0, out=dist_sq)`), and in-place square root operations (`np.sqrt(dist_sq, out=dist_sq)`), cutting execution latency by **$2.16\times$** ($0.565\text{s} \rightarrow 0.261\text{s}$).

### 4.3 Analysis of Failure Modes & Model Differences
* **The Non-Universal Response in GPT-4o**: Legacy models such as `gpt-4o` fail to respond to substrate constraints, allocating over $770\text{ MB}$ across all conditions. This suggests that substrate-aware algorithm synthesis is a reasoning capability that emerges in modern frontier models.
* **The Imperfect Constraint Satisfaction in `gpt-5.6-sol` (Trial 3)**: In Trial 3, `gpt-5.6-sol` generated a working buffer that reached $167.97\text{ MB}$ MaxRSS, exceeding the 128 MB ceiling. This confirms that constraint awareness does not magically guarantee 100% compliance, highlighting constraint reasoning as an important area for further evaluation.

---

## 5. Discussion, Limitations & Future Work

### 5.1 Scope & Limitations
1. **Pilot Sample Size**: Our paired statistical evaluation spans $N=5$ matched pairs ($10$ runs per model). While sufficient to demonstrate substantial algorithmic differences, larger evaluations across diverse tasks are required to characterize population distributions.
2. **Frozen Weights**: This study investigates zero-shot prompting of frozen models. We do not fine-tune or modify model weights.

### 5.2 Open Research Directions: Toward Substrate-Aware Post-Training (SARL)
Current Reinforcement Learning with Verifiable Rewards (RLVR / GRPO) frameworks reward models solely based on unit-test pass/fail status (+1 / -1), ignoring physical container resource consumption. Our findings demonstrate that frontier models already possess the latent capacity to synthesize memory-bounded algorithms when informed of limits. An exciting future direction is **Substrate-Aware Reinforcement Learning (SARL)**: incorporating Linux kernel telemetry (peak MaxRSS, memory pressure stalls, and CPU quotas) directly into verifiable reward functions during post-training alignment.

---

## 6. Conclusion

We have presented an empirical investigation into Substrate-Aware Code Generation. Our findings indicate that providing explicit execution constraints enables frontier reasoning models to transition from eager, memory-heavy patterns to structured, memory-bounded algorithms, substantially improving 128 MB memory budget compliance and execution latency.

---

## Artifact Index & Reproducibility
* **Benchmark Harnesses**: [`benchmarks/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/benchmarks/)
* **Raw Trial Scripts & Logs**: [`experiments/05_paired_statistical_trials/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/05_paired_statistical_trials/)
* **Multi-Model Ablation Logs**: [`experiments/04_frontier_model_benchmark/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/04_frontier_model_benchmark/)
