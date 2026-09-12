import pandas as pd
import json

df = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "amount_cents": "int64", "category": "string"},
)

mask = (df["account_id"].to_numpy() % 13) < 8
df = df.loc[mask]

mult = (df["account_id"].to_numpy() % 89) + 3
values = df["amount_cents"].to_numpy(dtype="int64") * mult.astype("int64")

result = pd.Series(values, index=df["category"].to_numpy()).groupby(level=0).sum()

out = {str(k): int(v) for k, v in sorted(result.items())}

print("TOTAL:" + json.dumps(out, sort_keys=True))
