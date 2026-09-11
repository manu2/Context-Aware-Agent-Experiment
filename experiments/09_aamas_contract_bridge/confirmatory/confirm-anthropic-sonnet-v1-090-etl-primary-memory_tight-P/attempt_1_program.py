import json
import pandas as pd

totals = {}

chunksize = 200_000
usecols = ["account_id", "category", "amount_cents"]
dtypes = {"account_id": "int64", "amount_cents": "int64", "category": "category"}

for chunk in pd.read_csv(
    "transactions.csv",
    usecols=usecols,
    dtype=dtypes,
    chunksize=chunksize,
):
    mask = (chunk["account_id"] % 11) < 7
    if not mask.any():
        continue
    sub = chunk.loc[mask]
    multiplier = (sub["account_id"] % 97) + 1
    weighted = sub["amount_cents"].astype("int64") * multiplier.astype("int64")
    grouped = weighted.groupby(sub["category"], observed=True).sum()

    for cat, val in grouped.items():
        cat = str(cat)
        totals[cat] = totals.get(cat, 0) + int(val)

result = {k: totals[k] for k in sorted(totals.keys())}
print("TOTAL:" + json.dumps(result))
