import pandas as pd
import json

totals = {}

chunksize = 200_000

for chunk in pd.read_csv(
    "transactions.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "category": "string", "amount_cents": "int64"},
    chunksize=chunksize,
):
    acc = chunk["account_id"].to_numpy()
    mask = (acc % 11) < 7
    if not mask.any():
        continue

    sub_acc = acc[mask]
    sub_amt = chunk["amount_cents"].to_numpy()[mask]
    sub_cat = chunk["category"].to_numpy()[mask]

    weight = (sub_acc % 97) + 1
    contrib = sub_amt.astype("int64") * weight.astype("int64")

    s = pd.Series(contrib, index=sub_cat)
    grouped = s.groupby(level=0).sum()

    for cat, val in grouped.items():
        totals[cat] = totals.get(cat, 0) + int(val)

result = {k: totals[k] for k in sorted(totals.keys())}
print("TOTAL:" + json.dumps(result))
