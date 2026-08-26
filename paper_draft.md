# Substrate-Aware Code Generation: Investigating How Execution Constraints Influence Algorithm Selection in AI Agents

**Authors**: Anonymous / Substrate Intelligence Research Group  
**Target Category**: arXiv `cs.DC` (Distributed & Cluster Computing) / `cs.AI` (Artificial Intelligence)  
**Code & Reproducibility Repository**: [GitHub: `Context-Aware-Agent-Experiment`](https://github.com/manu2/Context-Aware-Agent-Experiment)  

---

## Abstract

AI coding models can generate memory-intensive implementations when execution-resource limits are absent from the task specification. When tasked with high-dimensional scientific computing workloads inside resource-bounded environments (such as cloud micro-VMs or serverless containers), standard models often default to eager array materialization or unconstrained matrix products, exceeding the available memory budget.

In this work, we conduct a controlled empirical investigation into **Substrate-Aware Code Generation**—disclosing physical execution constraints (such as a 128 MB RAM budget and a 10.0s execution target) directly in the prompt without providing algorithmic guidance. Through replicated paired trials across frontier reasoning models (**Anthropic `claude-opus-5`** and **OpenAI `gpt-5.6-sol`**) alongside exploratory multi-model prompt sensitivity evaluations (**Google `gemini-3.7-flash`**, **Anthropic `claude-sonnet-5`**, and **OpenAI `gpt-4o`**), we observe:

1. **Qualitative Algorithmic Shift**: Exposing execution constraints induces models to replace full rectangular block evaluation with symmetry-aware, memory-bounded block evaluation, upper-trapezoid streaming, and in-place buffer recycling.
2. **Resource & Latency Reduction**: For `claude-opus-5`, substrate awareness reduces peak process resident set size (MaxRSS) from $238.40 \pm 49.94\text{ MB}$ to $93.57 \pm 7.56\text{ MB}$ ($2.55\times$ reduction) and wall-clock execution time from $0.7119\text{s}$ to $0.2677\text{s}$ ($2.66\times$ speedup), increasing 128 MB budget compliance from $0/5$ to $5/5$.
3. **Separability of Awareness and Constraint Satisfaction**: For `gpt-5.6-sol`, substrate awareness reduces average MaxRSS from $162.65 \pm 23.28\text{ MB}$ to $98.57 \pm 34.03\text{ MB}$ ($1.65\times$ reduction) with $4/5$ runs remaining within the 128 MB budget, demonstrating that constraint awareness and successful constraint-bounded synthesis are separable capabilities across model families.
4. **Vulnerability of Unanchored Natural Language Heuristics**: Generic natural language instructions (*"be memory efficient"*) produce unpredictable behaviors—causing `gemini-3.7-flash` to revert to an unvectorized scalar loop ($30.0\text{s}$) and `gpt-4o` to fail to adjust its memory footprint—whereas quantitative substrate boundaries guide models toward resource-efficient tile parameters.

---

## 1. Introduction & Research Question

As autonomous AI coding agents are increasingly deployed in resource-bounded cloud environments (such as Docker containers, AWS Lambda, and Kubernetes micro-VMs), the physical boundaries of the execution substrate become critical. However, standard agent harnesses typically isolate the LLM from the physical runtime: they supply the task description and tool schemas, but omit the memory ceilings and resource boundaries of the execution environment.

One possible explanation is that, when substrate information is absent, models rely more heavily on statistical priors learned from code written for computing environments that are typically less resource-constrained than the execution environment considered here. When an agent generates eager, full-memory allocations inside a strict 128 MB container, the Linux kernel terminates the process (`SIGKILL Exit 137`).

### 1.1 Research Question & Core Hypothesis
We investigate a straightforward empirical question:
> **Does exposing an AI coding agent to physical execution substrate constraints change the computational algorithms it chooses to synthesize?**

We hypothesize that providing explicit knowledge of substrate limits (e.g., `RAM limit: 128 MB`) induces models to reconsider default computational priors and perform zero-shot algorithmic restructuring—replacing full rectangular block evaluation with symmetry-aware, memory-bounded streaming—rather than merely tuning scalar constants within a fixed eager approach.

### 1.2 Prior Art & Systems Context
Our empirical investigation relates to existing literature across AI agent architectures, execution sandboxing, and memory-bounded numerical computing:
* **Agent Execution Sandboxes & Telemetry**: Frameworks such as *AgentSight* [1] and *ActPlane* [2] observe agent actions in external virtualization layers. While these systems collect post-hoc telemetry, standard agent architectures (e.g., ReAct [3], SWE-bench agents [4]) typically treat the execution container as an opaque black box during code synthesis.
* **Execution Feedback in Code Generation**: Recent literature demonstrates that execution-time error traces and unit-test feedback can guide post-hoc debugging loops (e.g., *RLEF* [5], *SafeCodeRL* [6]). In contrast, our investigation focuses on *zero-shot pre-execution constraint disclosure*, testing whether models can synthesize resource-bounded algorithms on the first attempt without entering multi-turn error-correction loops.
* **High-Performance Memory-Bounded Decomposition**: In scientific computing and systems engineering, out-of-core block tiling and upper-triangular symmetric evaluation are standard manual optimizations for matrix operations [7, 8]. We examine whether frontier LLMs autonomously select these specific structural decompositions when informed of container memory boundaries.

---

## 2. Experimental Methodology

### 2.1 Benchmark Task
We evaluate a representative high-dimensional scientific computing workload: computing the total sum of all pairwise Euclidean distances across an $8,000 \times 1,024$ single-precision matrix (`vectors.npy`, $32.768\text{ MB}$):
$$\text{Total Dist} = \sum_{i=0}^{N-1} \sum_{j=0}^{N-1} \|v_i - v_j\|_2$$
An unconstrained implementation that promotes data to float64 and materializes full rectangular intermediate matrices exceeds the 128 MB container ceiling.

### 2.2 Controlled Experimental Conditions
To isolate the effect of substrate information, we evaluate four prompt conditions without providing any algorithmic suggestions:
* **Condition A (Blind Baseline)**: Task specification only.
* **Condition B (Natural Language Advice)**: Task specification + generic optimization prompt (*"Please ensure your code is highly memory-efficient, fast, and avoids large allocations."*).
* **Condition C (1D Substrate Constraint)**: Task specification + explicit memory boundary (*"Execution environment: RAM limit: 128 MB."*).
* **Condition D (2D Substrate Constraint)**: Task specification + joint spatial and temporal constraint disclosure (*"Execution environment: RAM limit: 128 MB. Execution time limit: 10.0 seconds."*).

### 2.3 Measurement Protocol & Data Provenance
To ensure transparent reporting, we distinguish the experimental prompt condition from post-hoc memory measurement:
1. **Generative Trials & Code Archival**: During live generation trials, model responses were captured, extracted, and permanently archived to disk under `experiments/`.
2. **Post-Hoc OS Process MaxRSS Remeasurement**: Because initial Python-level `tracemalloc` instrumentation only tracked Python heap allocations and omitted native C-extension allocations (such as NumPy contiguous arrays), all archived trial scripts were independently re-executed in isolated subprocesses using standard OS-level resource profiling (`resource.getrusage(RUSAGE_SELF).ru_maxrss`) via `experiments/05_paired_statistical_trials/profile_canonical_maxrss.py` to obtain peak process resident memory. Wall-clock execution time was measured during the same canonical post-hoc profiling runs.
3. **128 MB Resource-Budget Threshold**: A run is classified as budget-compliant when its independently measured process MaxRSS is below 128 MB. Scripts exhibiting measured MaxRSS $< 128\text{ MB}$ satisfy the budget boundary, while scripts allocating $> 128\text{ MB}$ exceed the threshold. Single-trial cross-model evaluations in Table 2 are exploratory and are not used to estimate model-level effect sizes.

---

## 3. Empirical Results

### 3.1 Paired Comparison: Independent OS MaxRSS Profiling (Anthropic `claude-opus-5` vs. OpenAI `gpt-5.6-sol`)

Table 1 reports the independent OS MaxRSS measurements and 128 MB budget compliance across the $N=5$ matched pairs of archived scripts (canonical dataset: `canonical_paired_results.json`):

```
======================================================================================================================
Table 1: Paired Substrate-Awareness Evaluation (Post-Hoc OS MaxRSS Profiling of Archived Scripts)
======================================================================================================================
Model & Trial      | Condition A: Blind MaxRSS | Condition D: Aware MaxRSS | Blind 128M Budget | Aware 128M Budget
----------------------------------------------------------------------------------------------------------------------
claude-opus-5 (T1) |         205.69 MB         |          82.48 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.270s)
claude-opus-5 (T2) |         162.95 MB         |          99.17 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.255s)
claude-opus-5 (T3) |         239.75 MB         |         104.38 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.244s)
claude-opus-5 (T4) |         291.78 MB         |          91.34 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.260s)
claude-opus-5 (T5) |         291.83 MB         |          90.47 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.310s)
----------------------------------------------------------------------------------------------------------------------
--> claude-opus-5 Aggregate:
    Peak MaxRSS:   Blind = 238.40 ± 49.94 MB   vs.   Aware =  93.57 ±  7.56 MB (2.55x Reduction)
    Wall Latency:  Blind =  0.7119 ±  0.2293s   vs.   Aware =  0.2677 ±  0.0228s (2.66x Speedup)
    128M Budget Compliance:       Blind = 0/5 (0%)    vs.   Aware = 5/5 (100%)
======================================================================================================================
gpt-5.6-sol   (T1) |         142.48 MB         |          78.09 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.255s)
gpt-5.6-sol   (T2) |         142.53 MB         |          92.48 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.283s)
gpt-5.6-sol   (T3) |         146.44 MB         |         165.72 MB         | 💥 Exceeds (>128M)| 💥 Exceeds (166 MB)
gpt-5.6-sol   (T4) |         186.42 MB         |          77.98 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.262s)
gpt-5.6-sol   (T5) |         195.36 MB         |          78.56 MB         | 💥 Exceeds (>128M)| ✅ Within Budget (0.247s)
----------------------------------------------------------------------------------------------------------------------
--> gpt-5.6-sol Aggregate:
    Peak MaxRSS:   Blind = 162.65 ± 23.28 MB   vs.   Aware =  98.57 ± 34.03 MB (1.65x Reduction)
    Wall Latency:  Blind =  0.5690 ±  0.0061s   vs.   Aware =  0.2608 ±  0.0121s (2.18x Speedup)
    128M Budget Compliance:       Blind = 0/5 (0%)    vs.   Aware = 4/5 (80%)
======================================================================================================================
```

---

### 3.2 Exploratory Multi-Model Prompt Sensitivity

Table 2 presents single-trial prompt sensitivity evaluations across four conditions (from initial exploratory benchmarking) to examine behavioral variation across model families:

```
=================================================================================================================================
Table 2: Exploratory Multi-Model Prompt Sensitivity Across 4 Experimental Conditions
=================================================================================================================================
Model Architecture       | Condition A (Blind)    | Condition B (Natural Language) | Condition C (1D: 128M) | Condition D (2D: 128M+10s) 
=================================================================================================================================
OpenAI GPT-5.6-Sol       | 100.47 MB / 0.630s     | 7.24 MB / 0.694s               | 10.22 MB / 0.606s      | 4.12 MB / 0.190s           
                         | (✅ Within Budget)     | (✅ Within Budget)             | (✅ Within Budget)     | (🏆 In-Place Buffer Tiling)
---------------------------------------------------------------------------------------------------------------------------------
Anthropic Claude Sonnet 5| 215.22 MB / 1.041s     | 77.28 MB / 0.376s              | 92.46 MB / 0.434s      | 122.91 MB / 0.386s         
                         | (💥 Exceeds 128M)      | (✅ Within Budget, B=500)      | (✅ Within Budget, B=500)| (✅ Within Budget, B=1000)
---------------------------------------------------------------------------------------------------------------------------------
Google Gemini 3.7 Flash  | 1,565.72 MB / 2.880s   | < 35 MB / >30.0s               | 32.03 MB / 30.0s       | 114.84 MB / 0.460s         
                         | (💥 Exceeds 128M)      | (⏱️ Timeout Abort)            | (⚠️ Slow Scalar Loop)  | (🏆 2D BLAS Block Tiling)  
---------------------------------------------------------------------------------------------------------------------------------
OpenAI GPT-4o (Legacy)   | 1,136.31 MB / 1.350s   | 770.36 MB / 0.720s             | 770.36 MB / 0.690s     | 770.41 MB / 0.680s         
                         | (💥 Exceeds 128M)      | (💥 Exceeds 128M)              | (💥 Exceeds 128M)      | (💥 Exceeds 128M)          
=================================================================================================================================
```

*(Note: Table 1 contains the replicated N=5 paired trials with OS MaxRSS re-profiling; Table 2 contains single-trial exploratory prompt sensitivity runs from the initial cross-model screening.)*

---

## 4. Algorithmic Transformations & Case Studies

To understand the mechanisms behind the resource reductions, we inspect the generated code directly:

### 4.1 Full Rectangular Blocking vs. Symmetry-Aware Streaming in `claude-opus-5`
* **Blind Condition**: While `claude-opus-5` uses row blocking ($B=512$), it promotes the matrix to `float64` (`Xd = np.ascontiguousarray(X, dtype=np.float64)`, $65.5\text{ MB}$) and computes full rectangular products ($B \times N$), pushing peak MaxRSS to **$205.69\text{ MB} - 291.83\text{ MB}$**.
* **Substrate-Aware Condition**: Under substrate disclosure, `claude-opus-5` retains `float32`, sets symmetric 2D block size to $\text{BLOCK} = 2000$, and synthesizes an upper-block-triangle loop with in-place buffer reuse:
  ```python
  # Generated by Claude Opus 5 under 128 MB constraint (Trial 1)
  for i0 in range(0, n, BLOCK):
      i1 = min(i0 + BLOCK, n)
      A = X[i0:i1]
      na = norms[i0:i1][:, None]
      for j0 in range(i0, n, BLOCK):
          j1 = min(j0 + BLOCK, n)
          B = X[j0:j1]
          nb = norms[j0:j1][None, :]
          C = A @ B.T
          C *= m2
          C += na
          C += nb
          np.maximum(C, 0, out=C)
          np.sqrt(C, out=C)
          s = float(C.sum(dtype=np.float64))
          total += s if i0 == j0 else 2.0 * s
          del C
  ```
  This reduces peak MaxRSS to **$93.57\text{ MB}$** on average, completing in **$0.268\text{s}$**.

### 4.2 In-Place Buffer Recycling in `gpt-5.6-sol`
Under substrate awareness, `gpt-5.6-sol` applies memory-saving idioms: using memory-mapped I/O (`mmap_mode="r"`), in-place distance clamping (`np.maximum(dist_sq, 0.0, out=dist_sq)`), and in-place square root operations (`np.sqrt(dist_sq, out=dist_sq)`), cutting execution latency by **$2.18\times$** ($0.569\text{s} \rightarrow 0.261\text{s}$).

### 4.3 Analysis of Failure Modes & Model Differences
* **Behavior in GPT-4o**: In this exploratory benchmark, `gpt-4o` did not exhibit a measurable response to the disclosed constraints, allocating over $770\text{ MB}$ across all conditions. This contrast motivates further investigation into whether substrate-sensitive algorithm selection depends on model capability, training, or prompting.
* **Imperfect Constraint Satisfaction in `gpt-5.6-sol` (Trial 3)**: In Trial 3, `gpt-5.6-sol` generated a working buffer that reached $165.72\text{ MB}$ MaxRSS, exceeding the 128 MB ceiling. This confirms that constraint awareness does not guarantee compliance in all stochastic runs, highlighting constraint reasoning as an important area for further evaluation.

---

## 5. Discussion, Limitations & Future Work

### 5.1 Discussion
Our findings demonstrate that providing explicit execution constraints enables frontier models to replace full rectangular block evaluation with symmetry-aware, memory-bounded streaming evaluation, substantially lowering peak resident memory. However, the observation that GPT-5.6-Sol produced an aware-condition trial exceeding 128 MB (4/5 compliance) and GPT-4o failed across all conditions highlights that substrate awareness does not guarantee constraint-bounded competence. Awareness and constraint-satisfying synthesis are separable capabilities that vary across model architectures.

### 5.2 Scope & Limitations
1. **Pilot Scale**: Our paired statistical evaluation spans $N=5$ matched pairs ($10$ runs per model). While demonstrating substantial algorithmic differences, larger evaluations across broader task suites are required to characterize population distributions.
2. **Frozen Model Weights**: This study evaluates zero-shot prompting of frozen models without fine-tuning.
3. **Causal Attribution**: We cannot establish the exact internal mechanism by which models respond to substrate context, nor can we prove that pretraining distribution is the sole causal source of unconditioned eager behavior.
4. **Post-Hoc Measurement**: MaxRSS was independently remeasured on archived scripts rather than captured natively during live cgroup execution.

### 5.3 Future Work
Promising directions for future research include:
1. **Broader Resource Dimensions**: Investigating agent behavior under CPU quotas, GPU VRAM limits, storage I/O throughput, and network bandwidth boundaries.
2. **Dynamic Runtime Feedback**: Providing real-time telemetry updates during execution rather than static prompt injection.
3. **Substrate-Aware Training & Alignment**: Exploring whether integrating operating system telemetry (cgroup peaks, memory pressure events) into verifiable reward functions during post-training (RLVR/GRPO) improves native constraint compliance.

---

## 6. Conclusion

We have presented an empirical investigation into Substrate-Aware Code Generation. Our findings show that explicitly exposing physical execution constraints causes frontier AI coding models to reconsider default computational strategies and synthesize structured, memory-bounded algorithms, substantially improving 128 MB resource threshold compliance and execution speed.

---

## Artifact Index & Reproducibility
* **Benchmark Harnesses**: [`benchmarks/`](benchmarks/)
* **Canonical Paired MaxRSS Results**: [`experiments/05_paired_statistical_trials/canonical_paired_results.json`](experiments/05_paired_statistical_trials/canonical_paired_results.json)
* **MaxRSS Profiling Script**: [`experiments/05_paired_statistical_trials/profile_canonical_maxrss.py`](experiments/05_paired_statistical_trials/profile_canonical_maxrss.py)
* **Raw Trial Scripts & Logs**: [`experiments/05_paired_statistical_trials/`](experiments/05_paired_statistical_trials/)
* **Multi-Model Ablation Logs**: [`experiments/04_frontier_model_benchmark/`](experiments/04_frontier_model_benchmark/)

---

## References

[1] S. Zhang et al., "AgentSight: System-Level Observability for AI Agents Using eBPF," *arXiv preprint arXiv:2508.02736*, 2025.  
[2] H. Liu et al., "ActPlane: Declarative Sandboxing and Runtime Verification for Code-Executing Agents," *USENIX OSDI*, 2024.  
[3] S. Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," *International Conference on Learning Representations (ICLR)*, 2023.  
[4] C. E. Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?," *International Conference on Learning Representations (ICLR)*, 2024.  
[5] X. Chen et al., "RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement Learning," *arXiv preprint arXiv:2410.02089*, 2024.  
[6] Z. Wang et al., "SafeCodeRL: Security-Constrained Multi-Agent Reinforcement Learning for Trustworthy LLM-Generated Software," *Sensors*, vol. 26, no. 12, pp. 3812–3830, 2026.  
[7] G. H. Golub and C. F. Van Loan, *Matrix Computations*, 4th ed., Johns Hopkins University Press, 2013.  
[8] K. Goto and R. A. van de Geijn, "Anatomy of High-Performance Matrix Multiplication," *ACM Transactions on Mathematical Software (TOMS)*, vol. 34, no. 3, pp. 1–25, 2008.  

