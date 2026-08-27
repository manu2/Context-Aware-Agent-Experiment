# Fresh Generated-Code Transformation Audit

**Status:** Generated from archived scripts and metadata by `benchmarks/build_fresh_code_audit.py`.

This is a complete, source-linked feature audit of the 30 included fresh 128 MB direct-API scripts and 15 retained executable 96 MB local-sweep scripts. It records only observable source features; it does not infer model intent or claim that any individual feature alone caused a measured MaxRSS change.

The machine-readable companion is `experiments/06_replication/audit/fresh_code_transformation_audit.json`. Every row points to an archived source path and its SHA-256 digest. The raw scripts remain the authoritative record; the complete evidence package must be committed and release-tagged before public submission.

## Classification rules

- **Input mode:** `numpy_mmap` only when source explicitly supplies `mmap_mode=` to `np.load`; `numpy_load` when it calls `np.load` without that token.
- **Named blocking:** true only when source contains a named block/batch/chunk/tile parameter or an associated `range` expression. It does not say that the program is optimally bounded.
- **Output reuse/reset:** syntactic detection of `out=` or `.fill()` respectively.
- **Symmetry-related terms:** syntactic detection of `triu`, `tril`, upper/lower-triangle text, or a `* 2` expression; it is not a correctness proof.
- **AST parseability:** Python AST parsing under the audit interpreter. This is not a runtime compatibility test. The known Claude `opus_rep04_A` Python-3.9 runtime compatibility failure remains a recorded first-pass failure.

## 128 MB direct-API paired cohort

| Model | Pair | Blind features | Disclosed features | Observed RSS (MB), blind -> disclosed | Notes |
|---|---|---|---|---:|---|
| claude-opus-5 | `opus_rep02` | numpy_mmap, named-block, out-buffer, float32/float64 | numpy_load, named-block, out-buffer, float32/float64 | 206.02 -> 107.48 |  |
| claude-opus-5 | `opus_rep03` | numpy_mmap, named-block, out-buffer, float32/float64 | numpy_load, no-named-block, out-buffer, float32/float64 | 168.59 -> 102.80 |  |
| claude-opus-5 | `opus_rep04` | numpy_load, named-block, out-buffer, float64 | numpy_load, no-named-block, out-buffer, float32/float64 | 19.95 -> 105.56 | Blind source failed on the pinned Python 3.9 runtime; its measured RSS is not used in executable-pair means. |
| claude-opus-5 | `opus_rep05` | numpy_mmap, named-block, out-buffer, float32/float64 | numpy_load, named-block, out-buffer, float32/float64 | 345.33 -> 111.86 |  |
| claude-opus-5 | `opus_rep06` | numpy_mmap, named-block, out-buffer, float32/float64 | numpy_mmap, named-block, out-buffer, float32/float64 | 305.97 -> 111.38 |  |
| gpt-5.6-sol | `gpt_rep01` | numpy_mmap, named-block, out-buffer, Float64/float32/float64 | numpy_mmap, named-block, out-buffer, float32/float64 | 113.06 -> 65.83 |  |
| gpt-5.6-sol | `gpt_rep02` | numpy_mmap, named-block, out-buffer, float32/float64 | numpy_mmap, named-block, out-buffer, float32/float64 | 179.92 -> 60.00 |  |
| gpt-5.6-sol | `gpt_rep03` | numpy_mmap, named-block, out-buffer, Float64/float32/float64 | numpy_mmap, named-block, out-buffer, float32/float64 | 113.53 -> 54.20 |  |
| gpt-5.6-sol | `gpt_rep04` | numpy_mmap, named-block, out-buffer, float32/float64 | numpy_mmap, named-block, out-buffer, float32/float64 | 65.70 -> 87.64 |  |
| gpt-5.6-sol | `gpt_rep05` | numpy_load, named-block, out-buffer, Float64/float32/float64 | numpy_mmap, named-block, out-buffer, float32/float64 | 120.92 -> 55.38 |  |
| gemini-3.7-flash | `gemini_rep01` | numpy_load, named-block, out-buffer, float32/float64 | numpy_load, named-block, out-buffer, float32/float64 | 306.38 -> 124.91 |  |
| gemini-3.7-flash | `gemini_rep02` | numpy_load, named-block, out-buffer, float32/float64 | numpy_load, named-block, out-buffer, float32/float64 | 367.06 -> 170.31 |  |
| gemini-3.7-flash | `gemini_rep03` | numpy_load, no-named-block, out-buffer, float64 | numpy_mmap, named-block, out-buffer, float32 | 671.52 -> 216.05 |  |
| gemini-3.7-flash | `gemini_rep04` | numpy_load, named-block, out-buffer, float32/float64 | numpy_load, named-block, out-buffer, float32 | 549.95 -> 114.34 |  |
| gemini-3.7-flash | `gemini_rep05` | numpy_load, named-block, out-buffer, float64 | numpy_mmap, named-block, out-buffer, float32/float64 | 366.89 -> 165.19 |  |

## 96 MB condition-level extension

These are independently sampled condition-level 96 MB-aware scripts, not matched triples with the 128 MB pairs. All were locally profiled for observed RSS; no OS cgroup admission or kill was used for this table.

| Model | Retained trial | Source features | Observed RSS (MB) | Correct |
|---|---|---|---:|---|
| claude-opus-5 | `opus96_rep01_D` | numpy_load, named-block, out-buffer, float32/float64 | 62.47 | yes |
| claude-opus-5 | `opus96_rep02_D` | numpy_load, named-block, out-buffer, float32/float64 | 82.11 | yes |
| claude-opus-5 | `opus96_rep04_D` | numpy_load, named-block, out-buffer, float32/float64 | 89.56 | yes |
| claude-opus-5 | `opus96_rep06_D` | numpy_load, named-block, out-buffer, float32/float64 | 121.77 | yes |
| claude-opus-5 | `opus96_rep07_D` | numpy_mmap, named-block, out-buffer, float32/float64 | 81.94 | yes |
| gpt-5.6-sol | `gpt96_rep01_D` | numpy_mmap, named-block, out-buffer, float32/float64 | 62.42 | yes |
| gpt-5.6-sol | `gpt96_rep02_D` | numpy_mmap, named-block, out-buffer, float32/float64 | 63.98 | yes |
| gpt-5.6-sol | `gpt96_rep03_D` | numpy_mmap, named-block, out-buffer, float32/float64 | 70.58 | yes |
| gpt-5.6-sol | `gpt96_rep04_D` | numpy_mmap, named-block, out-buffer, float32/float64 | 53.25 | yes |
| gpt-5.6-sol | `gpt96_rep05_D` | numpy_mmap, named-block, out-buffer, float32/float64 | 54.17 | yes |
| gemini-3.7-flash | `gemini96_rep01_D` | numpy_mmap, named-block, out-buffer, float32/float64 | 81.31 | yes |
| gemini-3.7-flash | `gemini96_rep02_D` | numpy_load, named-block, out-buffer, float32 | 85.83 | yes |
| gemini-3.7-flash | `gemini96_rep03_D` | numpy_mmap, named-block, out-buffer, float64 | 205.25 | yes |
| gemini-3.7-flash | `gemini96_rep04_D` | numpy_mmap, named-block, out-buffer, float32/float64 | 89.28 | yes |
| gemini-3.7-flash | `gemini96_rep05_D` | numpy_load, named-block, out-buffer, float32/float64 | 130.62 | yes |

## Reproduction

```bash
.venv/bin/python3 benchmarks/build_fresh_code_audit.py --overwrite
```

The command fails if a retained source or metadata file is missing. It does not call a model API or modify any raw artifact.
