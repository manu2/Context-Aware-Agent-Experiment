import pandas as pd
import json

df = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "amount_cents": "int64"},
)

mask = (df["account_id"].to_numpy() % 13) < 8
sub = df.loc[mask]

weights = (sub["account_id"].to_numpy() % 89) + 3
values = sub["amount_cents"].to_numpy() * weights

result = pd.Series(values, index=sub["category"]).groupby(level=0).sum()

out = {str(k): int(v) for k, v in sorted(result.items())}

print("TOTAL:" + json.dumps(out, sort_keys=True))
