import pandas as pd
import json

df = pd.read_csv("transactions.csv", usecols=["account_id", "category", "amount_cents"])

mask = (df["account_id"] % 11) < 7
sub = df.loc[mask].copy()

weight = (sub["account_id"] % 97) + 1
sub["weighted"] = sub["amount_cents"].astype("int64") * weight.astype("int64")

result = sub.groupby("category")["weighted"].sum()

out = {str(k): int(v) for k, v in sorted(result.items())}

print("TOTAL:" + json.dumps(out, sort_keys=True))
