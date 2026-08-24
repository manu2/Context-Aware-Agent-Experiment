# AGENTS.md: CONTEXT & INSTRUCTIONS FOR AI AGENTS

Welcome to **Project Aether-Bus / SCAC (Substrate & Self-Telemetry Conditioned Agentic Computation)**.  
This document serves as the authoritative guide for any AI coding or research agent operating in this repository.

---

## 1. Project Purpose & Core Research Thesis

### Core Thesis
Autonomous AI coding agents (such as those in Jeff Dean's *Discovery Loop*) currently suffer from **"Silicon Blindness"**—they treat execution containers as infinite black boxes, leading to eager memory allocations, kernel OOM kills (`SIGKILL` Exit 137), and wasteful retry loops.

Instead of post-hoc error recovery, **SCAC** projects physical hardware limits (RAM ceilings, CPU quotas) and runtime telemetry (tool reliability, token budgets) directly into the agent's inference state. We investigate whether this enables autonomous agents to select memory-bounded algorithms (chunking, streaming) on their first attempt.

---

## 2. Document Map & Repository Index

All agents operating in this codebase MUST read and maintain the following key files:

| File Path | Description | Responsibility / Maintenance Rule |
|---|---|---|
| [`AGENTS.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/AGENTS.md) | **This file.** Agent guidelines, document index, and codebase rules. | Update whenever new workflow rules or architecture shifts occur. |
| [`RESEARCH_ROADMAP.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/RESEARCH_ROADMAP.md) | **Master Research Architecture.** Contains the 4D Self-Telemetry (SST) spec and 3-Phase Roadmap (Phase 1 Foil Test $\rightarrow$ Phase 2 Closed Loop $\rightarrow$ Phase 3 Systems Paper). | Update when expanding research scope or adding new experimental metrics. |
| [`EXECUTION_TRACKER.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/EXECUTION_TRACKER.md) | **Live Deployment & Execution Log.** Stage-by-stage tracker for GCP provisioning, execution, and teardown. | Must be updated **in real time** as deployment steps are executed. |
| [`handover.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/handover.md) | Initial research brief & background context (Jeff Dean / Discovery Loop rationale). | Read-only reference document. |
| [`week1_foil_test.py`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/week1_foil_test.py) | **Phase 1 Production Harness.** Zero-middleware script running 10 paired trials (20 LLM runs) inside a 128MB `cgroup v2` sandbox. | Maintain fail-closed pre-flight assertions and robust error handling. |
| [`requirements.txt`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/requirements.txt) | Python dependencies (`numpy`, `pandas`). | Keep minimal to avoid heavy container build steps. |
| [`phase1_csv_experiment_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/phase1_csv_experiment_report.md) | **Phase 1 Experimental Report.** Factually audited report on the 9 paired CSV trials (66.7% optimization shift, 2.22x speedup). | Primary empirical baseline report. |
| [`phase2_euclidean_single_trial_report.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/phase2_euclidean_single_trial_report.md) | **Phase 2 Single-Trial Baseline Report.** Factually audited report on the Pairwise Euclidean Distance task (Exit 137 SIGKILL OOM vs Exit 0 32.03MB Success). | Phase 2 empirical baseline report. |
| [`local_experiments/prompt_ablation_study/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/local_experiments/prompt_ablation_study/REPORT.md) | **Local Prompt Ablation & Sensitivity Study.** Self-contained local suite testing 4 prompt variants (Blind vs 128M vs 2GB vs 128M+10s). | Proves Quantitative Boundary Sensitivity & SOTA 2D Block Tiling. |
| [`.agents/skills/systems-research-benchmarking/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/.agents/skills/systems-research-benchmarking/SKILL.md) | **SOTA Systems Benchmarking Skill.** Statistical tests (McNemar, Wilcoxon, Cohen's d) & RSS profiling. | Project workspace skill. |
| [`.agents/skills/top-tier-paper-authoring/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/.agents/skills/top-tier-paper-authoring/SKILL.md) | **Top-Tier Paper Authoring Skill.** OSDI/MLSys/NeurIPS manuscript structure & narrative framing. | Project workspace skill. |
| [`.agents/skills/kernel-telemetry-cgroupv2/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/.agents/skills/kernel-telemetry-cgroupv2/SKILL.md) | **Linux cgroup v2 Telemetry Skill.** MemoryMax enforcement & `memory.events.local: high` tracking. | Project workspace skill. |
| [`.agents/skills/llm-agent-telemetry-eval/`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/.agents/skills/llm-agent-telemetry-eval/SKILL.md) | **LLM Agent Evaluation Skill.** Trajectory metrics (FPCR, ADR, TEF) & prompt injection protocols. | Project workspace skill. |

---

## 3. Strict Operating Guidelines for Agents

### 1. Documentation & Plan Synchronization
Whenever you perform an execution step, discover an edge case, or modify the architecture, you **MUST** update [`EXECUTION_TRACKER.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/EXECUTION_TRACKER.md) and/or [`RESEARCH_ROADMAP.md`](file://<LOCAL_USER_HOME>/projects/vibe-coding/Context-Aware-Agent-Experiment/RESEARCH_ROADMAP.md) immediately.

### 2. Fail-Closed Experimental Integrity
All experimental harnesses must include positive-control pre-flight checks (e.g. testing a 150MB allocation against a 128MB limit). Never disable preflight safety assertions to force a script to pass.

### 3. Model Standard
The primary target model for experiments is **`gemini-3.7-flash`** via the Google Generative Language v1beta REST API:
`https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent?key=${GEMINI_API_KEY}`

### 4. Cloud Cost Management
When executing GCP tasks via `gcloud`:
- Use cost-effective VM instances (`e2-medium` on Ubuntu 24.04 LTS).
- Run the experiment immediately upon provisioning.
- Fetch output artifacts (`results.json`, `summary_report.md`).
- **Immediately terminate/delete the VM** (`gcloud compute instances delete ... --quiet`) to prevent lingering costs.
