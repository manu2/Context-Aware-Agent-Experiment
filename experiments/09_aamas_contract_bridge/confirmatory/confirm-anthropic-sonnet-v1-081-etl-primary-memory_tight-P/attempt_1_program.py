import pandas as pd
import json
from collections import defaultdict

sums = defaultdict(int)

usecols = ["account_id", "category", "amount_cents"]
dtypes = {"account_id": "int64", "category": "category", "amount_cents": "int64"}

for chunk in pd.read_csv(
    "transactions.csv",
    usecols=usecols,
    dtype=dtypes,
    chunksize=200_000,
):
    mask = (chunk["account_id"] % 11) < 7
    if not mask.any():
        continue
    sub = chunk.loc[mask]
    weight = (sub["account_id"] % 97) + 1
    contrib = sub["amount_cents"].astype("int64") * weight.astype("int64")
    grouped = contrib.groupby(sub["category"], observed=True).sum()
    for cat, val in grouped.items():
        sums[str(cat)] += int(val)

result = {k: sums[k] for k in sorted(sums.keys())}
print("TOTAL:" + json.dumps(result))
