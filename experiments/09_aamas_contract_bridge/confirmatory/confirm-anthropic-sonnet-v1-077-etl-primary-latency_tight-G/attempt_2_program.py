import pandas as pd
import json

totals = {}

usecols = ["account_id", "category", "amount_cents"]
dtypes = {"account_id": "int64", "amount_cents": "int64"}

for chunk in pd.read_csv(
    "transactions.csv",
    usecols=usecols,
    dtype=dtypes,
    chunksize=1_000_000,
    engine="c",
    memory_map=True,
):
    acc = chunk["account_id"].to_numpy()
    mod11 = acc % 11
    mask = mod11 < 7
    if not mask.any():
        continue

    sub_acc = acc[mask]
    amt = chunk["amount_cents"].to_numpy()[mask]
    cats = chunk["category"].to_numpy()[mask]

    weight = (sub_acc % 97) + 1
    weighted = amt * weight

    s = pd.Series(weighted, index=cats)
    grouped = s.groupby(level=0).sum()

    for cat, val in grouped.items():
        if cat in totals:
            totals[cat] += int(val)
        else:
            totals[cat] = int(val)

print("TOTAL:" + json.dumps(totals, sort_keys=True))
