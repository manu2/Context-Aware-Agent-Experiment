import json
import pandas as pd


def main():
    totals = {}
    chunksize = 500_000

    for chunk in pd.read_csv(
        'transactions.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        dtype={'account_id': 'int64', 'category': 'str', 'amount_cents': 'int64'},
        chunksize=chunksize,
    ):
        acc = chunk['account_id']
        mask = (acc % 11) < 7
        if not mask.any():
            continue

        sub_acc = acc[mask]
        sub_cat = chunk.loc[mask, 'category']
        sub_amt = chunk.loc[mask, 'amount_cents']

        weight = (sub_acc % 97) + 1
        val = sub_amt * weight

        for cat, s in val.groupby(sub_cat).sum().items():
            totals[cat] = totals.get(cat, 0) + int(s)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == '__main__':
    main()
