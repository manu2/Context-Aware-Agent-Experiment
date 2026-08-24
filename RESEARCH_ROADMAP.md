# SCAC / PROJECT AETHER-BUS: RESEARCH ROADMAP & SYSTEM SPECIFICATION

**Project Title:** Substrate & Self-Telemetry Conditioned Agentic Computation (SST-SCAC)  
**Authors/Lead:** Research & Architecture Team  
**Status:** Phase 2 Complete → Phase 3 (Multi-Model Expansion & Paper Finalization)  
**Confidentiality:** 🔒 **PRIVATE** until arXiv preprint is published (author priority protection)

---

## 1. Executive Summary & Problem Thesis

### 1.1 The Motivating Problem ("Silicon Blindness")
As AI agents evolve into high-throughput autonomous execution loops (e.g., Jeff Dean's *Discovery Loop* for parallel scientific experimentation), they are deployed across heterogeneous virtualized sandboxes (128MB micro-VMs to multi-core containers). Currently, LLM agents treat every execution container as an unconstrained, infinite black box:
1. **Silicon Blindness**: The agent writes naive, memory-heavy code (e.g., eager `pd.read_csv()` on an 85MB file or large matrix multiplication).
2. **Silent Kernel Termination**: The Linux kernel immediately triggers an Out-Of-Memory (OOM) kill (`SIGKILL` / Exit Code 137).
3. **The Wasted Retry Loop**: The agent receives an opaque error string (`Process Exited with Code 137`), writes a conversational apology, and retries the exact same heavy algorithm until token budgets or context windows collapse.

### 1.2 Prior Art Differentiation
* **AgentSight (ACM PACMI, 2025)**: eBPF observability for human/compliance audits (post-hoc, no feedback loop to LLM during inference).
* **ActPlane (Eunomia, 2026)**: BPF-LSM security firewall (hard halt on violation, no recovery or substrate context).
* **SCAC & SST Framework (Ours)**: Exposes hardware constraints and real-time execution telemetry directly into the LLM's inference context as a first-class input to enable proactive strategy selection (chunking, streaming, out-of-core tiling, tool routing).

---

## 2. Theoretical Architecture: 4-Dimensional Self-Telemetry (SST)

We expand basic substrate awareness into a comprehensive **4D Self-Telemetry Agent (SST-Agent)** model:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 4D SUBSTRATE & SELF-TELEMETRY AGENT (SST)                   │
│                                                                             │
│ 1. SUBSTRATE CONSTRAINTS     2. TOKEN & CONTEXT ECONOMICS                   │
│ • RAM Limit / Peak RSS        • Remaining Context Window & Token Velocity    │
│ • CPU Quotas & Throttling     • API Rate Limit Headroom (TPM / RPM)         │
│                                                                             │
│ 3. TOOL RELIABILITY           4. COMPUTATIONAL / TOOL DECOMPOSITION          │
│ • Tool Failure Rates & Errors • Monolithic vs. Granular Tool Cost Ratio     │
│ • Execution Latency (P50/P99) • Dynamic Tool Selection & Fallback Routing   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Key Research Findings to Date

### 3.1 Telemetry Dimensionality Hierarchy (CRITICAL DISCOVERY)
Through empirical testing we have established a telemetry sensitivity hierarchy:

| Condition | Telemetry Injected | Agent Behavior | Outcome |
|---|---|---|---|
| **Blind** (0D) | None | Naive eager allocation (full matrix, `pd.read_csv()`) | ❌ OOM SIGKILL Exit 137 |
| **Natural Language** | "Be memory efficient" | Vague caution but no structural change | ❌ Timeout / No algorithmic shift |
| **1D (RAM only)** | `RAM limit: 128 MB` | Over-optimization (scalar row-by-row loops) | ⚠️ Correct but timeout (too slow) |
| **2D (RAM + CPU)** | `RAM limit: 128 MB, CPU quota: 10s` | **2D Block Tiling** (balanced memory × speed) | ✅ Pareto-optimal pass (0.63s, 69.82MB) |
| **1D (2GB — high ceiling)** | `RAM limit: 2 GB` | Cautious optimization (streaming/chunking) | ✅ Agent still optimizes even with generous limit |

### 3.2 Quantitative Boundary Sensitivity
- Even a generous 2GB RAM hint causes the agent to optimize (proving it's the **awareness** of a limit, not the tightness, that triggers behavioral change)
- Natural language advice ("be memory efficient") is insufficient — agents need **quantitative telemetry**

### 3.3 First-Pass Correctness Rate (FPCR)
- Phase 1 CSV: 66.7% optimization shift in aware condition
- Phase 2 Euclidean: 100% divergence (OOM vs success) in single trial
- Phase 2 Euclidean 10-trial: Consistent divergence across trials
- Local Ablation: 4/4 prompt variants show distinct behavioral signatures

---

## 4. Project Roadmap & Phasing

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PROJECT ROADMAP PHASING                         │
│                                                                        │
│  [PHASE 1: THE "FOIL CAN FLY" SIGNAL TEST]          ✅ COMPLETE        │
│  • Pure A/B baseline test (10 paired trials = 20 LLM runs)             │
│  • Result: 66.7% optimization shift, 2.22x speedup                     │
│  • Artifact: week1_foil_test.py                                        │
│                                                                        │
│  [PHASE 2: MULTI-DIMENSIONAL & CLOSED-LOOP TELEMETRY] ✅ COMPLETE      │
│  • Single-trial: Exit 137 OOM vs Exit 0 Success (32.03MB)              │
│  • 10-trial benchmark: Consistent divergence                           │
│  • Local Prompt Ablation: 4 variants (Blind/128M/2GB/2D 128M+10s)     │
│  • Natural Language vs Telemetry: NL advice → timeout, telemetry → ok  │
│                                                                        │
│  [PHASE 3: MULTI-MODEL EXPANSION & PAPER]     ◄── CURRENT FOCUS       │
│  • Multi-model benchmarking: Claude, GPT-4o, DeepSeek                  │
│  • 15-task benchmark suite (matrix + graph + dataframe + text)          │
│  • Statistical significance testing (p-values, Cohen's d)              │
│  • arXiv preprint → Conference submission (OSDI/MLSys/NeurIPS)         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Phase 3 Requirements (From Peer Review Feedback — Score: 6/10 → Target: 8.5/10)

### 5.1 Multi-Model Diversity (CRITICAL GAP)
All current results are from **Gemini 3.7 Flash only**. Reviewers require evidence across model families:

| Model | Provider | API Access | Status |
|---|---|---|---|
| Gemini 3.7 Flash | Google AI Studio / Vertex AI | ✅ Free tier + Vertex AI | ✅ Complete (all phases) |
| Claude Opus 4.6 / Sonnet 4 | Anthropic | ⚠️ Needs `ANTHROPIC_API_KEY` | 🔲 Not started |
| GPT-4o | OpenAI | ⚠️ Needs `OPENAI_API_KEY` ($5 min) | 🔲 Not started |
| DeepSeek V4-Flash | DeepSeek | ⚠️ Needs `DEEPSEEK_API_KEY` (cheapest) | 🔲 Not started |

**Access Strategy:**
- **Local subagent testing**: If `invoke_subagent` tool becomes available, can test Claude Opus 4.6 (current chat model) with zero API cost by spawning context-isolated subagents
- **API keys**: Anthropic trial credits (free on signup), DeepSeek ($0.14/1M tokens — cheapest option), OpenAI ($5 minimum prepay)
- **Script**: `multi_model_benchmark.py` is ready for all 4 providers

### 5.2 Task Diversity (15-Task Suite)
Current tasks are all matrix/CSV focused. Need expansion to:

| Category | Tasks | Status |
|---|---|---|
| **Matrix Operations** | Pairwise Euclidean Distance, Dot Product Sum, SVD/PCA | ✅ 2/3 done |
| **CSV/DataFrame** | Large CSV Aggregation, Multi-file Join, Pivot Table | ✅ 1/3 done |
| **Graph Algorithms** | BFS/DFS on large adjacency matrix, PageRank, Connected Components | 🔲 Not started |
| **Text Processing** | N-gram counting on large corpus, TF-IDF, String matching | 🔲 Not started |
| **Sorting/Search** | External merge sort, Top-K extraction, Binary search on large file | 🔲 Not started |

### 5.3 Statistical Rigor
- Paired t-tests or Wilcoxon signed-rank tests for matched pairs
- Cohen's d effect sizes
- McNemar's test for binary pass/fail outcomes
- **Minimum**: p < 0.05 with ≥10 paired trials per condition per model

---

## 6. Publication Strategy

### 6.1 Timeline
1. **Immediate**: Expand multi-model results (Claude, GPT-4o, DeepSeek)
2. **Week 1**: 15-task benchmark suite with statistical tests
3. **Week 2**: Paper revision incorporating reviewer feedback
4. **Week 3**: arXiv preprint submission (establishes author priority)
5. **Post-arXiv**: Target MLSys 2027 or NeurIPS 2027 Systems Track

### 6.2 Key Artifacts
- [`paper_draft.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/paper_draft.md) — Current 6-page draft
- [`reviewer_feedback.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/reviewer_feedback.md) — Simulated Senior Area Chair review (6/10 → 8.5/10 roadmap)
- [`multi_model_benchmark.py`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/multi_model_benchmark.py) — Multi-provider benchmark harness

---

## 7. Repository File Index

| File | Description | Status |
|---|---|---|
| `week1_foil_test.py` | Phase 1 production harness (10 paired CSV trials) | ✅ Frozen |
| `week2_closed_loop_test.py` | Phase 2 closed-loop harness (Euclidean distance) | ✅ Frozen |
| `single_test_A_blind.py` / `single_test_B_aware.py` | Phase 1 single-trial scripts | ✅ Frozen |
| `single_test_EUC_A_blind.py` / `single_test_EUC_B_aware.py` | Phase 2 single-trial scripts | ✅ Frozen |
| `test_prompt_variants_locally.py` | Local 4-variant ablation harness | ✅ Frozen |
| `multi_model_benchmark.py` | Multi-model (Gemini/Claude/GPT/DeepSeek) benchmark | ✅ Ready |
| `run_peer_reviewer.py` | Automated peer review simulation via LLM API | ✅ Ready |
| `local_experiments/prompt_ablation_study/` | Local ablation results + reproduction script | ✅ Complete |
| `paper_draft.md` | Research paper draft (SCAC framework) | 🔄 In revision |
| `reviewer_feedback.md` | Simulated peer review (6/10 score) | ✅ Complete |
| `foil_runs/` | Phase 1 GCE trial artifacts (20 scripts) | ✅ Archived |
| `foil_runs_euclidean/` | Phase 2 GCE trial artifacts | ✅ Archived |

---

## 8. Progress Tracker & Task Checklist

### Completed
- [x] Research Thesis & Handover Brief (`handover.md`)
- [x] Phase 1 Test Harness (`week1_foil_test.py`) — 10 paired trials on GCE
- [x] Phase 1 Report: 66.7% optimization shift, 2.22x speedup
- [x] Phase 2 Single-Trial Verification: Exit 137 vs Exit 0
- [x] Phase 2 10-Trial Benchmark on GCE
- [x] Local Prompt Ablation Study: 4 variants proving telemetry hierarchy
- [x] Natural Language vs Quantitative Telemetry comparison
- [x] Paper draft v1 (`paper_draft.md`)
- [x] Simulated peer review (`reviewer_feedback.md`, 6/10)
- [x] Multi-model benchmark script (`multi_model_benchmark.py`)

### In Progress / Next Steps
- [ ] **Multi-model testing**: Run Claude Opus 4.6 via subagent or API key
- [ ] **Multi-model testing**: Run GPT-4o and DeepSeek via API keys
- [ ] **15-task benchmark suite**: Add graph, text, and sorting tasks
- [ ] **Statistical significance**: Paired tests, p-values, Cohen's d across all conditions
- [ ] **Paper revision**: Incorporate reviewer feedback for 8.5/10 score
- [ ] **arXiv preprint**: Submit for author priority
