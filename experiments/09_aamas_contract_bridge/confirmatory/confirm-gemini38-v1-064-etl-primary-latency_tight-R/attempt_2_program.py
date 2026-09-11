import json
import pandas as pd


def main():
    totals = {}

    for chunk in pd.read_csv(
        'transactions.csv',
        chunksize=500_000,
        dtype={'category': str},
        keep_default_na=False,
    ):
        acc = chunk['account_id'].to_numpy()
        mask = (acc % 11) < 7
        if not mask.any():
            continue

        sub_acc = acc[mask]
        sub_amt = chunk['amount_cents'].to_numpy()[mask]
        sub_cat = chunk['category'].to_numpy()[mask]

        weight = (sub_acc % 97) + 1

        # Use Python arbitrary-precision integers to ensure exact product & sum
        prod = sub_amt.astype(object) * weight.astype(object)

        chunk_totals = pd.Series(prod).groupby(sub_cat, sort=False).sum()

        for cat, val in chunk_totals.items():
            totals[cat] = totals.get(cat, 0) + int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == '__main__':
    main()
