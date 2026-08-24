---
name: llm-agent-telemetry-eval
description: >-
  SOTA LLM agent trajectory evaluation, self-telemetry state injection, and multi-turn behavioral auditing.
  Use when designing agent evaluation loops, tracking token velocity/economics, classifying failure taxonomies,
  and injecting real-time tool reliability index or memory pressure telemetry into model inference context.
---

# LLM Agent Trajectory & Self-Telemetry Evaluation (SOTA Standard)

This skill provides protocols for measuring agent trajectory efficiency, self-telemetry state injection, and multi-turn strategy adaptation.

---

## 1. 4D Self-Telemetry State Injection Format

When injecting self-telemetry into an LLM agent prompt/context, use structured, zero-ambiguity key-value blocks:

```text
[EXECUTION SUBSTRATE & SELF-TELEMETRY]
- Memory Ceiling: 128 MB RAM (Swap: Disabled)
- Current Heap Overhead: 32 MB
- Token Window Remaining: 12,400 tokens / 128k
- Tool Reliability Index:
  * Tool_A (Pandas In-Memory): 35% Success Rate | P99 Latency: 4200ms
  * Tool_B (Line Streaming):   98% Success Rate | P99 Latency: 180ms
```

---

## 2. Failure Taxonomy & Trajectory Metrics

### 2.1 Categorical Failure Taxonomy
1. **OOM Kill (Exit 137)**: Code exceeded physical cgroup v2 RAM ceiling.
2. **Context Window Exhaustion**: Repeated retry loops filled context window with redundant code revisions and opaque traceback error strings.
3. **Tool Failure Thrashing**: Agent continuously invoked an unstable tool despite repeated failures.
4. **Token Inefficiency**: Agent wrote verbose, heavy scripts when a single-line memory-bounded pipe or iterator was sufficient.

### 2.2 Quantitative Trajectory Metrics
- **First-Pass Completion Rate (FPCR)**: Percentage of tasks completed on Attempt 1 without requiring error recovery.
- **Algorithmic Divergence Rate (ADR)**: Percentage of paired runs where disclosing telemetry caused a structural shift in algorithmic approach.
- **Token Efficiency Factor (TEF)**: Total tokens consumed divided by task completion status.
