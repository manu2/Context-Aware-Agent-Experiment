import pandas as pd
import json

totals = {}

usecols = ["account_id", "category", "amount_cents"]
dtype = {"account_id": "int64", "amount_cents": "int64", "category": "category"}

for chunk in pd.read_csv(
    "transactions.csv",
    usecols=usecols,
    dtype=dtype,
    chunksize=200_000,
):
    acc = chunk["account_id"].to_numpy()
    mask = (acc % 11) < 7
    if not mask.any():
        continue

    sub_acc = acc[mask]
    weight = (sub_acc % 97) + 1
    amt = chunk["amount_cents"].to_numpy()[mask]
    cats = chunk["category"].to_numpy()[mask]

    weighted = amt.astype("int64") * weight.astype("int64")

    s = pd.Series(weighted, index=cats)
    grouped = s.groupby(level=0, sort=False).sum()

    for cat, val in grouped.items():
        totals[cat] = totals.get(cat, 0) + int(val)

result = {str(k): totals[k] for k in sorted(totals.keys())}

print("TOTAL:" + json.dumps(result))
