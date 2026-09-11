import json
import pandas as pd

df = pd.read_csv(
    "transactions.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "category": "string", "amount_cents": "int64"},
)

mask = (df["account_id"].to_numpy() % 11) < 7
sub = df.loc[mask]

weights = (sub["account_id"].to_numpy() % 97) + 1
values = sub["amount_cents"].to_numpy() * weights

result = pd.Series(values, index=sub["category"]).groupby(level=0).sum()

out = {str(k): int(v) for k, v in sorted(result.items())}

print("TOTAL:" + json.dumps(out, sort_keys=True))
