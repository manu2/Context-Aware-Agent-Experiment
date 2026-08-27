# 96 MB Enforced-cgroup Pilot

This is an exploratory one-pair extension, not a revision of the frozen 128 MB
direct-API study. It tests GPT-5.6-Sol under a stricter, explicitly enforced Linux
cgroup v2 limit.

| Item | Specification |
|---|---|
| Model | `gpt-5.6-sol`, direct OpenAI API |
| Pair | One blind A generation and one D generation told `RAM limit: 96 MB` and `Execution time limit: 10.0 seconds` |
| Execution host | Fresh Ubuntu 24.04 GCE VM |
| Memory enforcement | `systemd-run` service with `MemoryMax=96M` and `MemorySwapMax=0` |
| Time enforcement | `RuntimeMaxSec=10` |
| Positive control | A 150 MB allocation must produce a cgroup OOM event before either generated script is run |
| Primary outcome | Correct exit-zero cgroup survival; secondary outcomes are `memory.events`, `memory.peak`, wall time, and generated implementation |

The raw response, extracted script, local generation metadata, remote cgroup profile,
and positive-control profile are retained under `raw/`.

## v1.3 local observed-RSS sweep

The core question is whether disclosed substrate information changes generated code.
Accordingly, v1.3 uses the existing fresh direct-API GPT `rep01`–`rep05` blind and
128 MB-aware artifacts as reference distributions and adds five independently
generated `96 MB + 10 s` aware scripts. Each new script is executed in an isolated
local subprocess and measured with OS MaxRSS, wall time, correctness, and direct
code inspection. These are **not** matched three-condition triples and are not used
for a pooled hypothesis test. `<=96 MB` is an observed-RSS classification, not a
cgroup-survival assertion.

## v1.4 Claude and Gemini extension

v1.4 applies the identical local observed-RSS 96 MB-aware condition to five new
Claude Opus 5 and five new Gemini 3.7 Flash generations. Existing fresh direct-API
blind and 128 MB-aware cohorts remain the condition-level references. Claude uses
its provider-required default sampling policy; GPT and Gemini retain their frozen
direct-API settings. No new blind generations are requested.

## v1.5 Claude replacement rule

Two original Claude requests are retained but not executable observations:
`opus96_rep03_D` has an empty provider response and `opus96_rep05_D` ends partway
through a fenced program. Before any replacement is generated, the manifest
predeclares `opus96_rep06_D` and `opus96_rep07_D` with the identical model
configuration and prompt hash. The replacements correct response validity only;
they are not outcome-based exclusions, and the original raw responses and failed
profiles remain archived.

## Result: one paired pilot (2026-08-27)

The positive control was kernel OOM-killed (`systemd Result=oom-kill`) when it
allocated 150 MB under `MemoryMax=96M`; cgroup enforcement therefore passed before
the generated code was executed.

| Condition | Enforced outcome | Wall time | Interpretation |
|---|---|---:|---|
| A: Blind | `Result=oom-kill` | 0.248 s | The generated program loaded and promoted the matrix to float64; it did not survive the 96 MB cap. |
| D: told 96 MB + 10 s | `Result=timeout` | 10.086 s | The generated program chose a 500x500 float32 reusable work buffer and did not OOM during its 10-second execution, but it did not complete inside the stated time limit. |

This is **not** a successful correct-and-within-budget pair: both conditions failed
the joint memory-and-time target, for different reasons. It is evidence that the
96 MB prompt changed the generated implementation and avoided an immediate OOM in
this one run, but it is not evidence of successful 96 MB cgroup survival. The pilot
does not justify automatically running four more pairs with the same joint target.

Two aware API calls were made because the first response's local artifact directory
appeared empty for several minutes. Both later materialized. The manifest v1.2
retains the first aware response as the paired D member and permanently excludes the
later duplicate before either execution outcome was inspected.
