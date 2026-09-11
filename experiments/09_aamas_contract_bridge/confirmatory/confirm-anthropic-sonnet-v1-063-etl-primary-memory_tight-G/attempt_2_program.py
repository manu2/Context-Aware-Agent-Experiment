import pandas as pd
import json

totals = {}

chunksize = 200_000
usecols = ["account_id", "category", "amount_cents"]
dtypes = {"account_id": "int64", "amount_cents": "int64", "category": "string"}

for chunk in pd.read_csv(
    "transactions.csv",
    usecols=usecols,
    dtype=dtypes,
    chunksize=chunksize,
):
    acc = chunk["account_id"].to_numpy()
    mask = (acc % 11) < 7
    if not mask.any():
        continue

    sub_acc = acc[mask]
    sub_amount = chunk["amount_cents"].to_numpy()[mask]
    sub_cat = chunk["category"].to_numpy()[mask]

    weight = (sub_acc % 97) + 1
    value = sub_amount.astype("int64") * weight.astype("int64")

    sub_df = pd.DataFrame({"category": sub_cat, "value": value})
    grouped = sub_df.groupby("category")["value"].sum()

    for cat, val in grouped.items():
        totals[cat] = totals.get(cat, 0) + int(val)

result = {k: totals[k] for k in sorted(totals.keys())}
print("TOTAL:" + json.dumps(result))
