# AGENTS.md: CONTEXT & INSTRUCTIONS FOR AI AGENTS

Welcome to **Project Aether-Bus / SCAC (Substrate & Self-Telemetry Conditioned Agentic Computation)**.  
This document serves as the authoritative guide for any AI coding or research agent operating in this repository.

---

## 1. Project Purpose & Core Research Thesis

### Core Thesis
Autonomous AI coding agents (such as those in Jeff Dean's *Discovery Loop*) currently suffer from **"Silicon Blindness"**—they treat execution containers as infinite black boxes, leading to eager memory allocations, kernel OOM kills (`SIGKILL` Exit 137), and wasteful retry loops.

Instead of post-hoc error recovery, **SCAC** projects physical hardware limits (RAM ceilings, CPU quotas) and runtime telemetry directly into the agent's inference state. We investigate whether this enables autonomous agents to select memory-bounded algorithms (chunking, streaming, block-tiling) on their first attempt.

---

## 2. Document Map & Repository Index

All agents operating in this codebase MUST read and maintain the following key files:

| File Path | Description | Responsibility / Maintenance Rule |
|---|---|---|
| [`AGENTS.md`](AGENTS.md) | **This file.** Agent guidelines, document index, and codebase rules. | Update whenever new workflow rules or architecture shifts occur. |
| [`README.md`](README.md) | **Repository Overview & Quickstart.** Architecture, results summary, and navigation. | Keep aligned with current empirical results and directory structure. |
| [`RESEARCH_ROADMAP.md`](RESEARCH_ROADMAP.md) | **Master Research Architecture.** Contains 4D SST spec and multi-phase roadmap. | Update when expanding research scope or adding new experimental metrics. |
| [`EXECUTION_TRACKER.md`](EXECUTION_TRACKER.md) | **Live Deployment & Execution Log.** Stage-by-stage tracker for all completed runs. | Must be updated **in real time** as execution steps occur. |
| [`paper_draft.md`](paper_draft.md) | **Primary arXiv Manuscript.** Complete, self-contained publication paper. | Primary manuscript for preprint and conference filing. |
| [`docs/`](docs/) | **Granular Empirical Reports.** Detailed markdown reports for all phases & models. | Maintain individual reports for Phase 1, Phase 2, Frontier models, and Paired trials. |
| [`experiments/`](experiments/) | **Raw Code & Execution Traces.** 100% of generated Python scripts and JSON logs. | Never delete raw trial scripts; preserve full provenance. |
| [`benchmarks/`](benchmarks/) | **Executable Benchmark Harnesses.** Multi-model and GCE evaluation scripts. | Maintain fail-closed preflight assertions and robust error handling. |

---

## 3. Strict Operating Guidelines for Agents

### 1. Documentation & Plan Synchronization
Whenever you perform an execution step, discover an edge case, or modify the architecture, you **MUST** update [`EXECUTION_TRACKER.md`](EXECUTION_TRACKER.md) and [`RESEARCH_ROADMAP.md`](RESEARCH_ROADMAP.md) immediately.

### 2. Fail-Closed Experimental Integrity
All experimental harnesses must include positive-control pre-flight checks (e.g. testing a 150MB allocation against a 128MB limit). Never disable preflight safety assertions to force a script to pass.

### 3. Preserving Raw Artifacts & Provenance
Every test run, prompt variant, and generated script MUST be recorded to disk inside the appropriate `experiments/` subdirectory. Never delete historical execution runs.
