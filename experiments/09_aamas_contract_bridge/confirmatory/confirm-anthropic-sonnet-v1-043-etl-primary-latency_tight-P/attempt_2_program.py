import pandas as pd
import json

df = pd.read_csv(
    "transactions.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "amount_cents": "int64", "category": "category"},
    engine="c",
)

acc = df["account_id"].to_numpy()
mask = (acc % 11) < 7

if mask.any():
    weight = (acc[mask] % 97) + 1
    values = df["amount_cents"].to_numpy()[mask] * weight
    cats = df["category"].to_numpy()[mask]

    result = pd.Series(values).groupby(cats, sort=False).sum()
    result = result.astype("int64")
    out = {str(k): int(v) for k, v in result.items()}
else:
    out = {}

print("TOTAL:" + json.dumps(out, sort_keys=True))
