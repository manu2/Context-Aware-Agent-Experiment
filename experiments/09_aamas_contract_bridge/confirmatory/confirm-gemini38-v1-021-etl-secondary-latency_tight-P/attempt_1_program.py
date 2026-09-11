from collections import defaultdict
import json
import pandas as pd


def main():
    totals = defaultdict(int)

    for chunk in pd.read_csv(
        'transactions_secondary.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        dtype={
            'account_id': 'int64',
            'amount_cents': 'int64',
            'category': 'str',
        },
        keep_default_na=False,
        chunksize=250000,
    ):
        mask = (chunk['account_id'] % 13) < 8
        matched = chunk[mask]
        if matched.empty:
            continue

        multipliers = (matched['account_id'] % 89) + 3
        weighted_amounts = matched['amount_cents'] * multipliers

        grouped = weighted_amounts.groupby(matched['category']).sum()
        for cat, val in grouped.items():
            totals[cat] += int(val)

    sorted_totals = dict(sorted(totals.items()))
    print(f'TOTAL:{json.dumps(sorted_totals)}')


if __name__ == '__main__':
    main()
