---
name: top-tier-paper-authoring
description: >-
  Guidelines for authoring systems and GenAI research papers targeting top-tier conferences
  (OSDI, MLSys, NeurIPS Systems track, ICML, SOSP). Use when drafting paper outlines,
  formatting LaTeX manuscripts, framing research narratives (e.g. Discovery Loop / Jeff Dean context),
  structuring evaluation sections, and designing system architecture diagrams.
---

# Top-Tier Systems & GenAI Paper Authoring Guide

This skill provides authoring, narrative framing, and structural standards for publishing systems & AI research papers.

---

## 1. Abstract & Introduction Narrative Template

### 1.1 The 5-Element Abstract Formula
1. **Context & Contextual Pivot**: Autonomous LLM coding agents are increasingly deployed in high-throughput scientific discovery loops across heterogeneous containers.
2. **The Key Problem ("Silicon Blindness")**: Agents treat execution containers as unconstrained black boxes, triggering frequent kernel OOM kills (`SIGKILL` 137) and expensive context-depleting retry loops.
3. **Core Insight / SCAC Hypothesis**: Exposing physical substrate constraints (RAM ceilings, CPU quotas) directly into the agent's inference context induces proactive selection of memory-bounded algorithms (chunking/streaming) on the first pass.
4. **Methodology & Key Results**: We present **SCAC**, a substrate-conditioned evaluation framework. Across paired A/B trials under strict 128MB container caps, substrate awareness shifts algorithmic strategy in $X\%$ of runs and increases first-pass completion from $Y\%$ to $Z\%$.
5. **Impact**: Demonstrates that physical hardware projection eliminates wasted execution retries and establishes the foundation for hardware-aware multi-agent scheduling.

---

## 2. Standard Paper Structure (OSDI / MLSys / NeurIPS Track)

```
1. INTRODUCTION
   • Problem Statement & The "Silicon Blindness" Trap
   • Prior Art & Novelty Boundaries (vs AgentSight, ActPlane)
   • Summary of Contributions

2. MOTIVATION & PRELIMINARY STUDY
   • Empirical breakdown of agent retry costs & OOM failure modes
   • Memory footprint analysis (Eager DataFrames vs Streaming Iterators)

3. SYSTEM DESIGN: SCAC & SST FRAMEWORK
   • Substrate-Conditioned Prompt Injection Protocol
   • 4D Self-Telemetry Architecture (Hardware, Tokens, Tools, Economics)
   • cgroup v2 Runtime Pressure Signals (`memory.events.local: high`)

4. EVALUATION & EXPERIMENTAL RESULTS
   • Experimental Setup & Host VM Specifications (Ubuntu 24.04, systemd cgroup v2)
   • Baseline Comparison: Condition A (Blind) vs Condition B (Substrate-Aware)
   • Strategy Divergence Analysis & Model Sensitivity Matrix

5. RELATED WORK
   • Agent Execution Sandboxes & Observability (AgentSight, ActPlane)
   • Context Window Management & LLM Code Generation

6. CONCLUSION & FUTURE WORK
   • Aether-Bus Resource-Offer Protocol specification for cluster schedulers
```

---

## 3. Visualization & Table Standards

- **Baseline Comparison Table**: Present Paired Trials with Status, Execution Time (sec), Memory Peak (MB), and Algorithm Strategy.
- **Architecture Diagrams**: Use clean Mermaid or TikZ diagrams emphasizing dataflow between the Kernel/cgroup v2 layer, Telemetry Monitor, and LLM Inference Engine.
- **LaTeX Math Notation**: Format inline math with `\(...\)` or `$...$`, and display equations with `\[...\]` or `$$...$$`.
