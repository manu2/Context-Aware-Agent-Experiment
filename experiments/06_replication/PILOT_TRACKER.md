# Pilot Frontier 3-Model Replication Tracker & Execution Spec

**Date:** August 2026  
**Status:** Completed Pilot Execution (Proxy Subagents Mode)  
**Target Frontier Models:**
1. `claude-opus-5` (Subagent Tier: Pro)
2. `gpt-5.6-sol` (Subagent Tier: Inherit)
3. `gemini-3.7-flash` (Subagent Tier: Flash)

---

## 1. Execution Matrix (3 Models x 2 Conditions = 6 Isolated Trials)

| Trial ID | Model Target | Condition | Injected Telemetry | Isolation Mode | Status |
|---|---|---|---|---|---|
| `opus_pilot_A` | `claude-opus-5` | **Condition A (Blind)** | *None* | Isolated Subagent | ✅ COMPLETED |
| `opus_pilot_D` | `claude-opus-5` | **Condition D (2D Telemetry)** | RAM: 128 MB, Time: 10.0s | Isolated Subagent | ✅ COMPLETED |
| `gpt_pilot_A` | `gpt-5.6-sol` | **Condition A (Blind)** | *None* | Isolated Subagent | ✅ COMPLETED |
| `gpt_pilot_D` | `gpt-5.6-sol` | **Condition D (2D Telemetry)** | RAM: 128 MB, Time: 10.0s | Isolated Subagent | ✅ COMPLETED |
| `gemini_pilot_A` | `gemini-3.7-flash` | **Condition A (Blind)** | *None* | Isolated Subagent | ✅ COMPLETED |
| `gemini_pilot_D` | `gemini-3.7-flash` | **Condition D (2D Telemetry)** | RAM: 128 MB, Time: 10.0s | Isolated Subagent | ✅ COMPLETED |

---

## 2. Strict Experimental Rules & Safety Invariants

1. **Prompt Parity Assertion**:
   * Condition A prompt SHA-256: `9eb9236ca49a72a98cf743051f635dcaf09091a0f77f71fa386adae71bf694f2`
   * Condition D prompt SHA-256: `e425c0445d4b0a432ef4a5adeb90b4bb885c69de9a2f1d0b809523af756470b4`
   * Zero optimization hints in either condition (no mention of "chunking", "block size", "symmetry", or "streaming").
2. **Subprocess Isolation**:
   * Every script executed in a separate, isolated OS subprocess with `cwd="data"`.
   * Enforced single-threaded BLAS (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`).
3. **Correctness Verification**:
   * Ground truth target: `2895556144.199324` ($8,000 \times 1,024$ float32 matrix).
   * Relative error threshold: $\Delta_{\text{rel}} < 10^{-4}$ ($0.01\%$).
4. **Safety Watchdog Ceiling**:
   * 60.0s hard watchdog kill.
5. **Manuscript Invariant**:
   * `paper_draft.md` remains strictly unmodified until full review consensus.
