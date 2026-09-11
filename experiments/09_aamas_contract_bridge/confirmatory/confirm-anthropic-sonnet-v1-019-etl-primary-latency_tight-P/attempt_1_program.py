import pandas as pd
import json

df = pd.read_csv(
    "transactions.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "amount_cents": "int64", "category": "str"},
)

mask = (df["account_id"] % 11) < 7
df = df.loc[mask]

multiplier = (df["account_id"] % 97) + 1
weighted = df["amount_cents"] * multiplier

result = weighted.groupby(df["category"]).sum()

out = {str(k): int(v) for k, v in result.items()}
out_sorted = {k: out[k] for k in sorted(out.keys())}

print("TOTAL:" + json.dumps(out_sorted))
