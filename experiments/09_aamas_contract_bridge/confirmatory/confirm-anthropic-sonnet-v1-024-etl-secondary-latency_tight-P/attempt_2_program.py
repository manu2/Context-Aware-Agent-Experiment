import pandas as pd
import json

df = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "amount_cents": "int64", "category": "category"},
    engine="c",
)

acc = df["account_id"].to_numpy()
mask = (acc % 13) < 8

amt = df["amount_cents"].to_numpy()[mask]
mult = (acc[mask] % 89) + 3
weighted = amt * mult

cats = df["category"].to_numpy()[mask]

result = pd.Series(weighted).groupby(cats, observed=True).sum()

out = {str(k): int(v) for k, v in result.items()}
out = dict(sorted(out.items()))

print("TOTAL:" + json.dumps(out))
