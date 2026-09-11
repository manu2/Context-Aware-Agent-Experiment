import pandas as pd
import json
from collections import defaultdict

totals = defaultdict(int)

chunksize = 100000
for chunk in pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "category": "string", "amount_cents": "int64"},
    chunksize=chunksize,
):
    mask = (chunk["account_id"] % 13) < 8
    if not mask.any():
        continue
    sub = chunk.loc[mask]
    multiplier = (sub["account_id"] % 89) + 3
    weighted = sub["amount_cents"].astype("int64") * multiplier.astype("int64")
    grouped = weighted.groupby(sub["category"]).sum()
    for cat, val in grouped.items():
        totals[cat] += int(val)

result = {k: totals[k] for k in sorted(totals.keys())}
print("TOTAL:" + json.dumps(result))
