import pandas as pd
import json

df = pd.read_csv("transactions_secondary.csv")

mask = (df["account_id"] % 13) < 8
sub = df[mask]

weights = (sub["account_id"] % 89) + 3
values = sub["amount_cents"].astype(object) * weights.astype(object)

result = {}
for cat, val in zip(sub["category"], values):
    result[cat] = result.get(cat, 0) + int(val)

sorted_result = {k: result[k] for k in sorted(result.keys())}

print("TOTAL:" + json.dumps(sorted_result))
