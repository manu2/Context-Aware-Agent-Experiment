import pandas as pd
import json
from collections import defaultdict

totals = defaultdict(int)

for chunk in pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "amount_cents": "int64", "category": "str"},
    chunksize=200000,
):
    acc = chunk["account_id"].to_numpy()
    mask = (acc % 13) < 8
    if not mask.any():
        continue
    sub = chunk.loc[mask]
    mult = (sub["account_id"].to_numpy() % 89) + 3
    contrib = sub["amount_cents"].to_numpy(dtype=object) * mult.astype(object)
    grouped = pd.Series(contrib, index=sub["category"].to_numpy()).groupby(level=0).apply(lambda s: sum(s))
    for cat, val in grouped.items():
        totals[cat] += int(val)

result = {k: totals[k] for k in sorted(totals.keys())}
print("TOTAL:" + json.dumps(result))
