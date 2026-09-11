import pandas as pd
import json

df = pd.read_csv("transactions.csv")

mask = (df["account_id"].astype("int64") % 11) < 7
df = df.loc[mask]

weight = (df["account_id"].astype("int64") % 97) + 1
weighted = df["amount_cents"].astype("int64") * weight

result = weighted.groupby(df["category"]).sum()

out = {str(k): int(v) for k, v in sorted(result.items())}

print("TOTAL:" + json.dumps(out, sort_keys=True))
