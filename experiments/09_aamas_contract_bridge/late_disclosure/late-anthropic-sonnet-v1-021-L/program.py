import pandas as pd
import json
from collections import defaultdict

totals = defaultdict(int)

chunksize = 200_000
usecols = ['account_id', 'category', 'amount_cents']
dtypes = {'account_id': 'int64', 'amount_cents': 'int64', 'category': 'object'}

for chunk in pd.read_csv(
    'transactions.csv',
    usecols=usecols,
    dtype=dtypes,
    chunksize=chunksize
):
    acc = chunk['account_id'].to_numpy()
    mask = (acc % 11) < 7
    if not mask.any():
        continue

    sub_acc = acc[mask]
    sub_amount = chunk['amount_cents'].to_numpy()[mask]
    sub_cat = chunk['category'].to_numpy()[mask]

    weights = (sub_acc % 97) + 1

    acc_list = sub_acc.tolist()
    amount_list = sub_amount.tolist()
    cat_list = sub_cat.tolist()
    weight_list = weights.tolist()

    for cat, amt, w in zip(cat_list, amount_list, weight_list):
        totals[cat] += int(amt) * int(w)

result = {k: totals[k] for k in sorted(totals.keys())}
print("TOTAL:" + json.dumps(result))
