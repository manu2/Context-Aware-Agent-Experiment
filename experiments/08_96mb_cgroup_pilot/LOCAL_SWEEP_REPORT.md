# 96 MB Local Observed-RSS Sweep

**Scope:** This boundary-sensitivity extension tests implementation adaptation, not
cgroup survival. It neither revises nor pools with the frozen 128 MB direct-API
cohort.

## Design and counting

For each model, the existing fresh direct-API blind and `128 MB + 10 s` cohorts
(`rep01`–`rep05`, except Claude `rep02`–`rep06`) are separate condition-level
reference distributions. This extension adds five independently generated
`96 MB + 10 s` aware programs for GPT-5.6-Sol, Claude Opus 5, and Gemini 3.7 Flash.
Every retained script runs in the same isolated macOS Python 3.9.6 / NumPy 2.0.2
subprocess and records OS `RUSAGE_CHILDREN` MaxRSS, wall time, output, and
ground-truth correctness.

The generations are stochastic and are **not** matched three-condition
trajectories. Thus, the table makes descriptive condition-level comparisons, not
a pooled hypothesis test. `<=96 MB` means a correct, exit-zero program whose
locally observed MaxRSS is at most 96 MB; it does not assert cgroup admission or
enforcement.

Claude `opus96_rep03_D` returned an empty response and `opus96_rep05_D` ended
before completing a program. Both raw responses and failed profiles remain in the
archive. Before replacement generation, manifest v1.5 predeclared identical-prompt
`opus96_rep06_D` and `opus96_rep07_D`; those two valid replacements complete the
five executable Claude observations. This is response-validity handling, not
outcome-based selection.

## Results

| Model | Prompt condition | N | Mean observed MaxRSS | Correct / <=96 MB | Mean wall time |
|---|---|---:|---:|---:|---:|
| GPT-5.6-Sol | Blind (existing fresh reference) | 5 | 118.63 MB | 1/5 | 0.5507 s |
|  | 128 MB + 10 s (existing fresh reference) | 5 | 64.61 MB | 5/5 | 0.3282 s |
|  | 96 MB + 10 s (new) | 5 | 60.88 MB | 5/5 | 0.3582 s |
| Claude Opus 5 | Blind (existing fresh reference) | 5 | 256.48 MB* | 0/5 | 0.9109 s* |
|  | 128 MB + 10 s (existing fresh reference) | 5 | 107.82 MB | 0/5 | 0.3612 s |
|  | 96 MB + 10 s (new) | 5 | 87.57 MB | 4/5 | 0.3802 s |
| Gemini 3.7 Flash | Blind (existing fresh reference) | 5 | 452.36 MB | 0/5 | 1.0994 s |
|  | 128 MB + 10 s (existing fresh reference) | 5 | 158.16 MB | 0/5 | 0.3561 s |
|  | 96 MB + 10 s (new) | 5 | 118.46 MB | 3/5 | 0.3985 s |

`*` Claude's blind mean uses the four executable blind programs. `opus_rep04_A`
is retained as a first-pass Python 3.9 runtime-compatibility failure in the 0/5 denominator.

The retained new 96 MB observations are:

| Model | Trial IDs (MaxRSS MB) |
|---|---|
| GPT-5.6-Sol | `rep01` 62.42; `rep02` 63.98; `rep03` 70.58; `rep04` 53.25; `rep05` 54.17 |
| Claude Opus 5 | `rep01` 62.47; `rep02` 82.11; `rep04` 89.56; `rep06` 121.77; `rep07` 81.94 |
| Gemini 3.7 Flash | `rep01` 81.31; `rep02` 85.83; `rep03` 205.25; `rep04` 89.28; `rep05` 130.62 |

All 15 retained scripts were correct within the configured numerical tolerance and
finished below 10 seconds. Gemini `rep03` and `rep05`, and Claude `rep06`, are
important retained counterexamples to the stated 96 MB boundary.

## Code-level observation

The valid 96 MB-aware outputs all avoided materializing the full 8000-by-8000
distance matrix and used resource-relevant mechanisms such as bounded row/tile
blocks, upper-triangle symmetry, in-place operations, and/or memory-mapped input.
The specific block sizes and temporary-precision choices vary. Some scripts still
exceeded 96 MB locally despite their stated memory accounting, showing that
constraint disclosure shifts implementation choices but does not guarantee a
particular measured footprint.

Compared with blind references, all three new 96 MB condition means are lower.
Compared with the already-aware 128 MB reference, the means also decrease (GPT
64.61 to 60.88 MB; Claude 107.82 to 87.57 MB; Gemini 158.16 to 118.46 MB), but
these separate stochastic samples do not establish a deterministic or monotonic
per-generation response.

The separately archived Ubuntu cgroup pilot remains an operational diagnostic and
is not used in this table or in any local observed-RSS conclusion.
