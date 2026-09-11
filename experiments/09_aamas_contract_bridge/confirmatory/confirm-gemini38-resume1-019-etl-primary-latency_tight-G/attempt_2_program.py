from collections import defaultdict
import json
import numpy as np
import pandas as pd


def main():
    totals = defaultdict(int)
    chunksize = 1_000_000

    for chunk in pd.read_csv(
        'transactions.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        dtype={
            'account_id': np.int64,
            'category': str,
            'amount_cents': np.int64,
        },
        chunksize=chunksize,
        keep_default_na=False,
    ):
        acc = chunk['account_id'].to_numpy()
        mask = (acc % 11) < 7
        if not np.any(mask):
            continue

        f_acc = acc[mask]
        f_cents = chunk['amount_cents'].to_numpy()[mask]
        f_cat = chunk['category'].to_numpy()[mask]

        weights = (f_acc % 97) + 1

        # Check potential int64 overflow: 97 * max_cents * count
        max_cents = int(np.max(np.abs(f_cents))) if len(f_cents) > 0 else 0
        if max_cents > 90_000_000_000:
            weighted = weights.astype(object) * f_cents.astype(object)
            grouped = pd.Series(weighted, dtype=object).groupby(f_cat).sum()
        else:
            weighted = weights * f_cents
            grouped = pd.Series(weighted).groupby(f_cat).sum()

        for cat, val in grouped.items():
            totals[cat] += int(val)

    output = json.dumps(totals, sort_keys=True, separators=(',', ':'))
    print(f'TOTAL:{output}')


if __name__ == '__main__':
    main()
