import pandas as pd
import json

df = pd.read_csv(
    "transactions.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "category": "string", "amount_cents": "int64"},
)

mask = (df["account_id"] % 11) < 7
sub = df.loc[mask]

weight = (sub["account_id"] % 97) + 1
contrib = sub["amount_cents"] * weight

result = contrib.groupby(sub["category"]).sum()

out = {str(k): int(v) for k, v in result.items()}
out = dict(sorted(out.items()))

print("TOTAL:" + json.dumps(out))
