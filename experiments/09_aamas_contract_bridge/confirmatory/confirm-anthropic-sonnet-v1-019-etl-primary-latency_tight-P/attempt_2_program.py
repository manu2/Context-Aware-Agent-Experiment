import pandas as pd
import numpy as np
import json

usecols = ["account_id", "category", "amount_cents"]
dtypes = {"account_id": "int64", "amount_cents": "int64", "category": "category"}

totals = {}

chunksize = 500_000

for chunk in pd.read_csv(
    "transactions.csv",
    usecols=usecols,
    dtype=dtypes,
    chunksize=chunksize,
):
    acc = chunk["account_id"].to_numpy()
    mod11 = acc % 11
    mask = mod11 < 7
    if not mask.any():
        continue

    acc_f = acc[mask]
    amt_f = chunk["amount_cents"].to_numpy()[mask]
    cat_f = chunk["category"].to_numpy()[mask]

    multiplier = (acc_f % 97) + 1
    weighted = amt_f * multiplier

    # Group by category within this chunk using pandas groupby for speed
    sub = pd.DataFrame({"category": cat_f, "weighted": weighted})
    grouped = sub.groupby("category", observed=True)["weighted"].sum()

    for cat, val in grouped.items():
        cat = str(cat)
        totals[cat] = totals.get(cat, 0) + int(val)

result = {k: totals[k] for k in sorted(totals.keys())}
print("TOTAL:" + json.dumps(result))
