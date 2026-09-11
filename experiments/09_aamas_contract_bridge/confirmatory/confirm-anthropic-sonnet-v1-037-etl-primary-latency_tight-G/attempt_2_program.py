import pandas as pd
import json

totals = {}

dtype = {
    'account_id': 'int64',
    'category': 'category',
    'amount_cents': 'int64',
}

for chunk in pd.read_csv(
    'transactions.csv',
    usecols=['account_id', 'category', 'amount_cents'],
    dtype=dtype,
    chunksize=2_000_000,
):
    acc = chunk['account_id'].to_numpy()
    mod11 = acc % 11
    mask = mod11 < 7
    if not mask.any():
        continue

    acc_sel = acc[mask]
    amounts = chunk['amount_cents'].to_numpy()[mask]
    cats = chunk['category'].to_numpy()[mask]

    mult = (acc_sel % 97) + 1
    vals = amounts.astype('int64') * mult.astype('int64')

    sub_df = pd.DataFrame({'category': cats, 'val': vals})
    grp = sub_df.groupby('category', observed=True)['val'].sum()

    for cat, s in grp.items():
        totals[cat] = totals.get(cat, 0) + int(s)

result = {str(k): totals[k] for k in sorted(totals, key=lambda x: str(x))}
print("TOTAL:" + json.dumps(result))
