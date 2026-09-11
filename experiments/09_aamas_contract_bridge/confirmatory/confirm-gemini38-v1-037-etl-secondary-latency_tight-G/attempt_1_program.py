from collections import defaultdict
import json
import pandas as pd


def main():
    totals = defaultdict(int)
    chunk_size = 500_000

    for chunk in pd.read_csv(
        'transactions_secondary.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        dtype={
            'account_id': 'int64',
            'category': 'str',
            'amount_cents': 'int64',
        },
        na_filter=False,
        chunksize=chunk_size,
    ):
        mask = (chunk['account_id'] % 13) < 8
        if not mask.any():
            continue

        filtered = chunk.loc[mask]
        multiplier = (filtered['account_id'] % 89) + 3
        products = filtered['amount_cents'] * multiplier

        grouped = products.groupby(filtered['category']).sum()
        for cat, val in grouped.items():
            totals[str(cat)] += int(val)

    print(f'TOTAL:{json.dumps(totals, sort_keys=True)}')


if __name__ == '__main__':
    main()
