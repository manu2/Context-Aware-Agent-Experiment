# Gemini 3.8 Flash non-pooled pilot

This development pilot is used to freeze the confirmatory protocol and is never pooled with confirmatory evidence.

- Trajectories: 24
- Provider calls: 34
- Estimated API cost: $1.099
- Finish reasons: {'STOP': 34}

## Outcomes by condition

| Condition | N | First-pass suitable | Final suitable | Calls |
|---|---:|---:|---:|---:|
| P | 8 | 7/8 | 8/8 | 9 |
| R | 8 | 3/8 | 4/8 | 13 |
| G | 8 | 4/8 | 4/8 | 12 |

## Outcomes by cell

| Family | Environment | Condition | First | Final | Initial strategies |
|---|---|---:|---:|---:|---|
| etl | latency_tight | G | 2/2 | 2/2 | `{'pandas_chunked': 2}` |
| etl | latency_tight | P | 1/2 | 2/2 | `{'pandas_eager_or_vectorized': 2}` |
| etl | latency_tight | R | 1/2 | 2/2 | `{'stdlib_streaming': 2}` |
| etl | memory_tight | G | 2/2 | 2/2 | `{'pandas_chunked': 2}` |
| etl | memory_tight | P | 2/2 | 2/2 | `{'stdlib_streaming': 2}` |
| etl | memory_tight | R | 2/2 | 2/2 | `{'stdlib_streaming': 2}` |
| numerical | latency_tight | G | 0/2 | 0/2 | `{'blocked_or_streamed_matrix_product': 1, 'unblocked_matrix_product': 1}` |
| numerical | latency_tight | P | 2/2 | 2/2 | `{'blocked_or_streamed_matrix_product': 1, 'unblocked_matrix_product': 1}` |
| numerical | latency_tight | R | 0/2 | 0/2 | `{'unblocked_matrix_product': 2}` |
| numerical | memory_tight | G | 0/2 | 0/2 | `{'unblocked_matrix_product': 1, 'blocked_or_streamed_matrix_product': 1}` |
| numerical | memory_tight | P | 2/2 | 2/2 | `{'blocked_or_streamed_matrix_product': 2}` |
| numerical | memory_tight | R | 0/2 | 0/2 | `{'unblocked_matrix_product': 2}` |

## Gate reading

The proactive condition achieved 7/8 first-pass and 8/8 final suitability, compared with 3/8 and 4/8 for reactive discovery and 4/8 and 4/8 for generic efficiency guidance.
On the numerical task, proactive disclosure was suitable in all 4 trajectories while reactive and generic conditions were suitable in 0/4. On ETL, every condition ultimately completed, but the selected implementations differed with the envelope: proactive memory runs streamed, while proactive latency runs used Pandas and completed within the tighter time contract.
These are pilot observations, not confirmatory estimates. They support advancing to protocol freeze while retaining task-, environment-, and model-stratified analysis.
