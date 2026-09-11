import json
from collections import defaultdict
import pandas as pd

def main():
    totals = defaultdict(int)

    for chunk in pd.read_csv(
        'transactions_secondary.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        keep_default_na=False,
        chunksize=100000
    ):
        mask = (chunk['account_id'] % 13) < 8
        sub = chunk[mask]
        if sub.empty:
            continue

        weights = (sub['account_id'] % 89) + 3

        if sub['amount_cents'].dtype == object or sub['amount_cents'].abs().max() > 10**12:
            weighted = sub['amount_cents'].astype(object) * weights.astype(object)
        else:
            weighted = sub['amount_cents'] * weights

        for cat, val in weighted.groupby(sub['category']).sum().items():
            totals[str(cat)] += int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")

if __name__ == '__main__':
    main()
