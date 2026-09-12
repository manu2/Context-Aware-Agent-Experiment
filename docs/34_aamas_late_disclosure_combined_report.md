# AAMAS late-disclosure recovery extension: combined analysis

> Separately frozen extension over the 82 archived first-attempt failures in condition R. Development canary results are excluded.

Exact contract disclosure at recovery increased suitable recovery from **19/82** to **53/82**. Matched transitions were **35 improvements**, **1 regression**, **18 shared successes**, and **28 shared failures** (descriptive exact McNemar p = **1.0768417e-09**).

## Complete workflow

| Model | P first | P final | R first | R final: symptoms | R final: late contract |
|---|---:|---:|---:|---:|---:|
| gemini-3.8-flash | 24/32 | 25/32 | 5/32 | 8/32 | 30/32 |
| claude-sonnet-5 | 16/32 | 22/32 | 1/32 | 9/32 | 14/32 |
| gpt-5.6-sol | 24/32 | 25/32 | 8/32 | 16/32 | 23/32 |
| **All** | **64/96** | **72/96** | **14/96** | **33/96** | **67/96** |

## Interpretation

The exact execution contract is valuable both before action and after failure. Symptom-only recovery leaves the operational boundary implicit; revealing the boundary converts substantially more failures into suitable programs. Proactive disclosure achieves 64 suitable first attempts and avoids the failed execution and additional generation required by late disclosure. Late disclosure raises the corresponding R workflow to 67 final successes, showing that models can still adapt strongly when precise substrate information arrives after failure. The strongest system design therefore supplies the contract before planning and retains exact-contract recovery for residual failures.

The source failures comprised 24 OOM kills and 58 timeouts. L recovered 18/24 OOM-origin states and 35/58 timeout-origin states. No L execution was OOM-killed; the residual failures were 27 timeouts and 2 runtime/correctness errors.

The proactive workflow used 128 provider calls, versus 178 for the late-disclosure workflow—a difference of 50 calls.

Total estimated provider cost for the 82 L branches was **$3.297615**.
