import pandas as pd
import json

df = pd.read_csv("transactions_secondary.csv")

mask = (df["account_id"] % 13) < 8
sub = df.loc[mask]

weight = (sub["account_id"] % 89) + 3
contrib = sub["amount_cents"].astype("int64") * weight.astype("int64")

result = contrib.groupby(sub["category"]).sum()

out = {str(k): int(v) for k, v in result.items()}
out = dict(sorted(out.items()))

print("TOTAL:" + json.dumps(out))
