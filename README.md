# Project Aether-Bus: Substrate & Self-Telemetry Conditioned Agentic Computation (SCAC)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Target: arXiv](https://img.shields.io/badge/Target-arXiv%20cs.DC%20%2F%20cs.AI-red.svg)](paper_draft.md)
[![Status: Multi-Model Audited](https://img.shields.io/badge/Status-Multi--Model%20Audited-green.svg)](docs/)

> **Research Hypothesis**: Autonomous AI coding agents suffer from **"Silicon Blindness"**—they generate algorithms assuming infinite RAM and CPU, triggering fatal OS-level Out-Of-Memory kills (`SIGKILL Exit 137`) under container isolation (`cgroup v2`). Projecting physical hardware limits directly into the inference context enables zero-shot, memory-bounded algorithmic parameter selection on the first pass.

---

## 1. Multi-Model Empirical Benchmark Results (128 MB Sandbox)

Evaluated across **Google Gemini 3.7 Flash**, **Anthropic Claude Opus 5**, **OpenAI GPT-5.6-Sol**, and **Anthropic Claude Sonnet 5**:

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

## 2. Repository Layout & File Index

```
.
├── paper_draft.md                     # Complete arXiv manuscript (Self-contained)
├── AGENTS.md                          # Authoritative agent operating instructions
├── RESEARCH_ROADMAP.md                # 4D SST Architecture & multi-phase roadmap
├── EXECUTION_TRACKER.md               # Stage-by-stage live log of all completed stages
├── requirements.txt                   # Minimal Python dependencies
│
├── benchmarks/                        # Executable benchmark runners
│   ├── multi_model_benchmark.py       # Unified multi-model evaluator
│   ├── week1_foil_test.py             # Phase 1 GCE CSV harness
│   ├── week2_closed_loop_test.py      # Phase 2 GCE Euclidean harness
│   ├── test_prompt_variants_locally.py# 4-prompt sensitivity tester
│   └── run_peer_reviewer.py           # Simulated peer reviewer harness
│
├── data/                              # Benchmark datasets
│   └── vectors.npy                    # 8000x1024 float32 matrix (32.8 MB)
│
├── docs/                              # Granular empirical reports
│   ├── 00_handover_research_brief.md  # Original research context & motivation
│   ├── 01_phase1_gemini_csv_report.md # Phase 1 CSV 9-trial report (66.7% shift)
│   ├── 02_phase2_gemini_euclidean_report.md # Phase 2 Euclidean report (90% shift)
│   ├── 03_prompt_ablation_report.md   # Local 4-prompt sensitivity report
│   ├── 04_frontier_models_report.md   # Cross-frontier 4-condition ablation report
│   ├── 05_claude_opus_analysis_report.md # Deep dive into Claude Opus 5 precision vs OOM
│   ├── 06_statistical_paired_report.md# Formal 5-paired statistical report (p < 0.01)
│   └── 07_peer_reviewer_feedback.md   # Simulated Senior Area Chair evaluation
│
└── experiments/                       # 100% of all generated Python code & raw JSON traces
    ├── 01_csv_gce_phase1/             # 18 GCE trial scripts + results.json
    ├── 02_euclidean_gce_phase2/       # 20 GCE trial scripts + results.json
    ├── 03_prompt_ablation_local/      # Prompt ablation test scripts & comparison JSON
    ├── 04_frontier_model_benchmark/   # Raw scripts for Gemini, GPT-5.6-Sol, Claude Opus/Sonnet
    ├── 05_paired_statistical_trials/  # 20 paired trial scripts + raw execution JSONs
    └── 06_openai_gpt4o_baseline/      # Legacy GPT-4o test scripts & baseline report
```

---

## 3. Quickstart & Reproduction

```bash
# 1. Clone & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run the 5-paired statistical verification benchmark
python3 experiments/05_paired_statistical_trials/run_paired_trials.py

# 3. Simulate peer review evaluation on the paper draft
python3 benchmarks/run_peer_reviewer.py
```