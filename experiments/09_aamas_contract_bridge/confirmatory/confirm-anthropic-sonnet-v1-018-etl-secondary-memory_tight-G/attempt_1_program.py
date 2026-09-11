import pandas as pd
import json

df = pd.read_csv("transactions_secondary.csv", usecols=["account_id", "category", "amount_cents"])

mask = (df["account_id"] % 13) < 8
sub = df.loc[mask]

weights = (sub["account_id"] % 89) + 3
weighted = sub["amount_cents"] * weights

result = weighted.groupby(sub["category"]).sum()

out = {str(k): int(v) for k, v in sorted(result.items())}

print("TOTAL:" + json.dumps(out))
