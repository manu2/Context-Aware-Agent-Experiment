import pandas as pd
import json

df = pd.read_csv('transactions.csv')

mask = (df['account_id'] % 11) < 7
sub = df[mask]

weights = (sub['account_id'] % 97) + 1
values = sub['amount_cents'].astype('int64') * weights.astype('int64')

result = {}
for cat, val in zip(sub['category'], values):
    result[cat] = result.get(cat, 0) + int(val)

sorted_result = {k: result[k] for k in sorted(result.keys())}

print("TOTAL:" + json.dumps(sorted_result))
