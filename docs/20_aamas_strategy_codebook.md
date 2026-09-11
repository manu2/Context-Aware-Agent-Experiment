# AAMAS strategy codebook v0.1

**Status:** frozen before confirmatory generation  
**Implementation:** `src/aether_contract_bridge/strategy.py`

This codebook records observable implementation structure in generated Python
programs. It is a secondary behavioral outcome. Correctness and operational
suitability are always determined by execution, oracle comparison, cgroup memory
evidence, and the frozen wall-time contract; a static label never overrides an
execution outcome.

## Numerical labels

- `eager_global_matrix`: global matrix-product or full broadcast construction
  without an explicit outer blocking loop.
- `blocked_matrix_product`: matrix products inside explicit iteration, including
  row blocks or two-dimensional tiles.
- `rowwise_or_scalar_streaming`: explicit iterative distance work without a
  matrix-product signature.
- `other`: no frozen signature matched; requires adjudication.
- `unparseable`: Python AST parsing failed; requires adjudication.

Orthogonal features are `memory_map`, `triangular_symmetry`, `in_place_update`,
and `float32_explicit`.

## ETL labels

- `dataframe_eager`: DataFrame CSV ingestion without an explicit `chunksize`.
- `dataframe_chunked`: DataFrame CSV ingestion with an explicit `chunksize`.
- `stdlib_streaming`: a standard-library CSV iterator consumed by a loop without
  explicit materialization.
- `stdlib_materialized`: explicit `readlines()` or list materialization of a CSV
  iterator.
- `other` and `unparseable`: require adjudication.

Orthogonal features are `pandas`, `explicit_chunksize`, `csv_iterator`, and
`explicit_materialization`.

## Adjudication rule

The classifier output and source hash are archived for every attempt. Only
`other` and `unparseable` labels receive manual adjudication. The adjudicator sees
the generated program but not its condition label or execution outcome, selects
one existing codebook label or records `unresolved`, and supplies a one-sentence
rationale. Labels are never invented after confirmatory generation.

## Pilot audit

The codebook classified all 34 archived Gemini 3.8 Flash pilot attempts without
an ambiguous first-attempt label. The first-attempt distribution captures the
expected behavioral distinctions: proactive memory-tight numerical programs were
both blocked; reactive numerical programs were all eager; proactive ETL programs
used standard-library streaming under the memory-tight envelope and eager Pandas
under the latency-tight envelope. These pilot observations freeze the codebook;
they are not pooled with confirmatory results.
