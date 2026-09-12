import pandas as pd
import json

df = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "amount_cents": "int64", "category": "string"},
)

mask = (df["account_id"] % 13) < 8
sub = df.loc[mask]

factor = (sub["account_id"] % 89) + 3
weighted = sub["amount_cents"] * factor

result = weighted.groupby(sub["category"]).sum()

out = {str(k): int(v) for k, v in result.items()}
out = dict(sorted(out.items()))

print("TOTAL:" + json.dumps(out))
