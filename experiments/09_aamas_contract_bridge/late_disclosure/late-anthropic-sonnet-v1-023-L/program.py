import pandas as pd
import json

# Read only necessary columns; let pandas infer efficient dtypes
df = pd.read_csv(
    'transactions.csv',
    usecols=['account_id', 'category', 'amount_cents'],
    dtype={'account_id': 'int64', 'amount_cents': 'int64', 'category': 'string'}
)

# Filter rows where account_id % 11 < 7
mod11 = df['account_id'].to_numpy() % 11
mask = mod11 < 7

acc = df['account_id'].to_numpy()[mask]
amt = df['amount_cents'].to_numpy()[mask]
cat = df['category'].to_numpy()[mask]

mult = (acc % 97) + 1
weighted = amt * mult  # int64 arithmetic, exact as long as no overflow

# Aggregate sums per category using pandas groupby (vectorized, fast)
result_df = pd.DataFrame({'category': cat, 'weighted': weighted})
sums = result_df.groupby('category', sort=True)['weighted'].sum()

out = {str(k): int(v) for k, v in sums.items()}

print("TOTAL:" + json.dumps(out, sort_keys=True))
