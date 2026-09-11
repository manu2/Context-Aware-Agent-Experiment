import pandas as pd
import json

df = pd.read_csv("transactions.csv")

mask = (df["account_id"] % 11) < 7
filtered = df.loc[mask].copy()

weight = (filtered["account_id"] % 97) + 1
filtered["weighted"] = filtered["amount_cents"].astype("int64") * weight.astype("int64")

grouped = filtered.groupby("category")["weighted"].sum()

result = {str(k): int(v) for k, v in sorted(grouped.items())}

print("TOTAL:" + json.dumps(result, sort_keys=True))
