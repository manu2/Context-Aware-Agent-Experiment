import pandas as pd
import json

df = pd.read_csv('transactions_secondary.csv', usecols=['account_id', 'category', 'amount_cents'])

mask = (df['account_id'] % 13) < 8
df = df.loc[mask]

weights = (df['account_id'] % 89) + 3
values = df['amount_cents'] * weights

result = values.groupby(df['category']).sum()

out = {str(k): int(v) for k, v in sorted(result.items())}

print("TOTAL:" + json.dumps(out))
