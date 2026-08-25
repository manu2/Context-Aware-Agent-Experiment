# Substrate-Aware Code Generation: Investigating How Execution Constraints Influence Algorithm Selection in AI Agents

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Target: arXiv](https://img.shields.io/badge/Target-arXiv%20cs.DC%20%2F%20cs.AI-red.svg)](paper_draft.md)
[![Status: Multi-Model Audited](https://img.shields.io/badge/Status-Multi--Model%20Audited-green.svg)](docs/)

> **Research Investigation**: Autonomous AI coding agents frequently generate code under the implicit assumption that execution environments possess unbounded memory, causing Out-Of-Memory (OOM) kills inside cloud micro-VMs. We investigate whether projecting physical execution substrate constraints (such as a 128 MB RAM ceiling) directly into inference context induces agents to synthesize memory-bounded, Pareto-efficient algorithms on their first attempt.

---

## 1. Primary Empirical Evidence: Paired Substrate-Awareness Benchmark

Formal paired evaluation across 10 live paired trials (20 live executions) comparing **Condition A (Blind)** and **Condition D (Substrate-Aware)**:

```
======================================================================================================================
Table 1: Paired Substrate-Awareness Benchmark (Condition A: Blind vs. Condition D: Substrate-Aware)
======================================================================================================================
Model & Trial      | Condition A: Blind MaxRSS | Condition D: Aware MaxRSS | Blind 128M Status | Aware 128M Status
----------------------------------------------------------------------------------------------------------------------
claude-opus-5 (T1) |         204.47 MB         |          78.48 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.265s)
claude-opus-5 (T2) |         164.28 MB         |          99.98 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.255s)
claude-opus-5 (T3) |         236.77 MB         |          91.47 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.244s)
claude-opus-5 (T4) |         307.38 MB         |          98.06 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.261s)
claude-opus-5 (T5) |         303.28 MB         |          85.47 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.315s)
----------------------------------------------------------------------------------------------------------------------
--> claude-opus-5 Aggregate:
    Peak MaxRSS:   Blind = 243.24 ± 55.67 MB   vs.   Aware =  90.69 ±  7.97 MB (2.68x Reduction)
    Wall Latency:  Blind =  0.6886 ±  0.1613s   vs.   Aware =  0.2680 ±  0.0246s (2.57x Speedup)
    128M Container Survivability:  Blind = 0/5 (0%)   vs.   Aware = 5/5 (100%)
======================================================================================================================
gpt-5.6-sol   (T1) |         142.33 MB         |          95.33 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.260s)
gpt-5.6-sol   (T2) |         142.38 MB         |          92.19 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.281s)
gpt-5.6-sol   (T3) |         148.48 MB         |         167.97 MB         | 💥 OOM (Exceeds)  | 💥 OOM (167 MB)
gpt-5.6-sol   (T4) |         196.72 MB         |          89.05 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.259s)
gpt-5.6-sol   (T5) |         199.56 MB         |          83.36 MB         | 💥 OOM (Exceeds)  | ✅ Pass (0.247s)
----------------------------------------------------------------------------------------------------------------------
--> gpt-5.6-sol Aggregate:
    Peak MaxRSS:   Blind = 165.89 ± 26.44 MB   vs.   Aware = 105.58 ± 31.44 MB (1.57x Reduction)
    Wall Latency:  Blind =  0.5646 ±  0.0053s   vs.   Aware =  0.2611 ±  0.0111s (2.16x Speedup)
    128M Container Survivability:  Blind = 0/5 (0%)   vs.   Aware = 4/5 (80%)
======================================================================================================================
```

---

## 2. Multi-Model Sensitivity Across 4 Experimental Conditions

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
│   └── run_peer_reviewer.py           # Local pre-flight audit script
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
│   ├── 06_statistical_paired_report.md# Formal paired statistical report
│   └── 08_rigorous_peer_review_audit.md # Peer review audit report
│
└── experiments/                       # 100% of all generated Python code & raw JSON traces
    ├── 01_csv_gce_phase1/             # 18 GCE trial scripts + results.json
    ├── 02_euclidean_gce_phase2/       # 20 GCE trial scripts + results.json
    ├── 03_prompt_ablation_local/      # Prompt ablation test scripts & comparison JSON
    ├── 04_frontier_model_benchmark/   # Raw scripts for Gemini, GPT-5.6-Sol, Claude Opus/Sonnet
    ├── 05_paired_statistical_trials/  # 20 paired trial scripts + raw execution JSONs
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

# 2. Run the paired verification benchmark
python3 experiments/05_paired_statistical_trials/run_paired_trials.py

# 3. Run the local manuscript pre-flight audit
python3 benchmarks/run_peer_reviewer.py
```