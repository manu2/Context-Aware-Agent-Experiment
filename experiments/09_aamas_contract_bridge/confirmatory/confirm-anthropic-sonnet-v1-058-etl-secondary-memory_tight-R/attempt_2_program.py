import pandas as pd
import json

totals = {}

chunksize = 200_000
usecols = ["account_id", "category", "amount_cents"]
dtype = {"account_id": "int64", "amount_cents": "int64", "category": "category"}

for chunk in pd.read_csv(
    "transactions_secondary.csv",
    usecols=usecols,
    dtype=dtype,
    chunksize=chunksize,
):
    mod13 = chunk["account_id"] % 13
    mask = mod13 < 8
    if not mask.any():
        continue
    sub = chunk.loc[mask]
    mult = (sub["account_id"].astype("int64") % 89) + 3
    weighted = sub["amount_cents"].astype("int64") * mult.astype("int64")
    grouped = weighted.groupby(sub["category"], observed=True).sum()
    for cat, val in grouped.items():
        totals[cat] = totals.get(cat, 0) + int(val)

result = {str(k): totals[k] for k in sorted(totals.keys())}
print("TOTAL:" + json.dumps(result))
