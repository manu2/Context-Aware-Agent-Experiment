import pandas as pd
import json

df = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "category": "str", "amount_cents": "int64"},
)

mask = (df["account_id"] % 13) < 8
sub = df.loc[mask]

weight = (sub["account_id"] % 89) + 3
weighted = sub["amount_cents"].astype("int64") * weight.astype("int64")

result = weighted.groupby(sub["category"]).sum()

out = {str(k): int(v) for k, v in sorted(result.items())}

print("TOTAL:" + json.dumps(out, sort_keys=True))
