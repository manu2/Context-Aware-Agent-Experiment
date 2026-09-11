import json
from collections import defaultdict
import pandas as pd


def main():
    totals = defaultdict(int)
    chunk_size = 1_000_000

    for chunk in pd.read_csv(
        'transactions.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        dtype={'account_id': 'int64', 'amount_cents': 'int64'},
        chunksize=chunk_size
    ):
        mask = (chunk['account_id'] % 11) < 7
        if not mask.any():
            continue

        filtered = chunk[mask]
        mult = (filtered['account_id'] % 97) + 1

        # Safeguard against int64 overflow for extremely large values
        max_abs = filtered['amount_cents'].abs().max()
        if max_abs < 90_000_000_000:
            prod = filtered['amount_cents'] * mult
        else:
            prod = filtered['amount_cents'].astype(object) * mult.astype(object)

        chunk_sum = prod.groupby(filtered['category'], observed=False).sum()
        for cat, val in chunk_sum.items():
            totals[str(cat)] += int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == '__main__':
    main()
