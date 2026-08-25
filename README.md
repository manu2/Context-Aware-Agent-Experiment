# Substrate-Aware Code Generation: Investigating How Execution Constraints Influence Algorithm Selection in AI Agents

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Target: arXiv](https://img.shields.io/badge/Target-arXiv%20cs.DC%20%2F%20cs.AI-red.svg)](paper_draft.md)
[![Status: Multi-Model Audited](https://img.shields.io/badge/Status-Multi--Model%20Audited-green.svg)](docs/)

> **Research Investigation**: Autonomous AI coding agents frequently generate code under the implicit assumption that execution environments possess unbounded memory, causing Out-Of-Memory (OOM) kills inside cloud micro-VMs. We investigate whether disclosing physical execution substrate constraints (such as a 128 MB RAM ceiling) directly into inference prompts induces agents to synthesize memory-bounded, resource-efficient algorithms on their first attempt.

---

## 1. Primary Empirical Evidence: Paired Substrate-Awareness Benchmark

Post-hoc operating system process memory profiling (`resource.getrusage(RUSAGE_SELF).ru_maxrss`) across the $N=5$ matched pairs of archived generated scripts (canonical dataset: [`canonical_paired_results.json`](file:///Users/manuagrawal/projects/vibe-coding/Context-Aware-Agent-Experiment/experiments/05_paired_statistical_trials/canonical_paired_results.json)):

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

## 2. Multi-Model Sensitivity Across 4 Experimental Conditions

```
=================================================================================================================================
Table 2: Exploratory Multi-Model Prompt Sensitivity Across 4 Experimental Conditions
=================================================================================================================================
Model Architecture       | Condition A (Blind)    | Condition B (Natural Language) | Condition C (1D: 128M) | Condition D (2D: 128M+10s) 
=================================================================================================================================
Anthropic Claude Opus 5  | 205.69 MB / 1.167s     | 82.50 MB / 0.738s              | 92.46 MB / 0.434s      | 82.48 MB / 0.270s          
                         | (💥 Exceeds 128M)      | (✅ Within Budget)             | (✅ Within Budget)     | (🏆 Upper-Trapezoid Stream)
---------------------------------------------------------------------------------------------------------------------------------
OpenAI GPT-5.6-Sol       | 142.48 MB / 0.572s     | 89.20 MB / 0.694s              | 91.50 MB / 0.606s      | 78.09 MB / 0.255s          
                         | (💥 Exceeds 128M)      | (✅ Within Budget)             | (✅ Within Budget)     | (🏆 In-Place Buffer Tiling)
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

---

## 3. Repository Layout & File Index

```
.
├── paper_draft.md                     # Complete arXiv manuscript (Self-contained)
├── AGENTS.md                          # Authoritative agent operating instructions
├── README.md                          # Repository overview & quickstart
├── RESEARCH_ROADMAP.md                # Research roadmap & hypothesis log
├── EXECUTION_TRACKER.md               # Stage-by-stage live log of all completed stages
├── requirements.txt                   # Minimal Python dependencies (numpy, pandas)
│
├── benchmarks/                        # Executable benchmark runners
│   ├── multi_model_benchmark.py       # Unified multi-model evaluator
│   ├── week1_foil_test.py             # Phase 1 GCE CSV harness
│   ├── week2_closed_loop_test.py      # Phase 2 GCE Euclidean harness
│   ├── test_prompt_variants_locally.py# 4-prompt sensitivity tester
│   └── run_peer_reviewer.py           # Numerical consistency checker
│
├── data/                              # Benchmark datasets
│   ├── vectors.npy                    # 8000x1024 float32 matrix (32.8 MB)
│   └── server_logs.txt                # 1,200,000 log records (82.4 MB)
│
├── docs/                              # Granular empirical reports
│   ├── 00_handover_research_brief.md  # Original research brief & context
│   ├── 01_phase1_gemini_csv_report.md # Phase 1 CSV 9-trial report
│   ├── 02_phase2_gemini_euclidean_report.md # Phase 2 Euclidean report
│   ├── 03_prompt_ablation_report.md   # Local 4-prompt sensitivity report
│   ├── 04_frontier_models_report.md   # Cross-frontier 4-condition ablation report
│   ├── 05_claude_opus_analysis_report.md # Deep dive into Claude Opus 5 precision vs OOM
│   ├── 06_statistical_paired_report.md# Formal paired report (canonical MaxRSS)
│   └── 08_rigorous_peer_review_audit.md # Peer review audit report
│
└── experiments/                       # 100% of all generated Python code & raw JSON traces
    ├── 01_csv_gce_phase1/             # 18 GCE trial scripts + results.json
    ├── 02_euclidean_gce_phase2/       # 20 GCE trial scripts + results.json
    ├── 03_prompt_ablation_local/      # Prompt ablation test scripts & comparison JSON
    ├── 04_frontier_model_benchmark/   # Raw scripts for Gemini, GPT-5.6-Sol, Claude Opus/Sonnet
    ├── 05_paired_statistical_trials/  # 20 paired trial scripts + canonical MaxRSS profiler & JSON
    ├── 06_openai_gpt4o_baseline/      # Legacy GPT-4o test scripts & baseline report
    └── 07_task3_log_stream_ablation/  # Task 3 log streaming scripts & profiling
```

---

## 4. Quickstart & Reproduction

```bash
# 1. Clone & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the canonical OS MaxRSS profiler on archived paired scripts
python3 experiments/05_paired_statistical_trials/profile_canonical_maxrss.py

# 3. Run the numerical consistency checker against paper_draft.md
python3 benchmarks/run_peer_reviewer.py
```