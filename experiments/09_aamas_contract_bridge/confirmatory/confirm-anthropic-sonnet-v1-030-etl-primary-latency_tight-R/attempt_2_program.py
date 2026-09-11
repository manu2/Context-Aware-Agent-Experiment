import pandas as pd
import json

# Read only the columns we need for efficiency
df = pd.read_csv(
    'transactions.csv',
    usecols=['account_id', 'category', 'amount_cents'],
    dtype={'account_id': 'int64', 'amount_cents': 'int64', 'category': 'string'}
)

# Filter rows where account_id % 11 < 7
mod11 = df['account_id'] % 11
mask = mod11 < 7

acc = df.loc[mask, 'account_id']
amt = df.loc[mask, 'amount_cents']
cat = df.loc[mask, 'category']

multiplier = (acc % 97) + 1
weighted = amt * multiplier

result = weighted.groupby(cat).sum()

out = {str(k): int(v) for k, v in result.items()}
out_sorted = dict(sorted(out.items()))

print("TOTAL:" + json.dumps(out_sorted))
