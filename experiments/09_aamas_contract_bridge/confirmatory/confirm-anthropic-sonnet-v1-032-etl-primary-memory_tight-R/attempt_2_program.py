import pandas as pd
import json

totals = {}

for chunk in pd.read_csv(
    'transactions.csv',
    chunksize=200_000,
    usecols=['account_id', 'category', 'amount_cents'],
    dtype={'account_id': 'int64', 'amount_cents': 'int64'}
):
    mod11 = chunk['account_id'] % 11
    mask = mod11 < 7
    if not mask.any():
        continue

    sub_account = chunk.loc[mask, 'account_id']
    sub_amount = chunk.loc[mask, 'amount_cents']
    sub_category = chunk.loc[mask, 'category']

    multiplier = (sub_account % 97) + 1
    value = sub_amount * multiplier

    grouped = value.groupby(sub_category).sum()

    for cat, val in grouped.items():
        totals[cat] = totals.get(cat, 0) + int(val)

result = {k: totals[k] for k in sorted(totals)}
print("TOTAL:" + json.dumps(result))
