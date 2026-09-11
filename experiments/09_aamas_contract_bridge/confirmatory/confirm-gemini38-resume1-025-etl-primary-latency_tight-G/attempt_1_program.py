import json
import pandas as pd

def main():
    totals = {}
    chunksize = 250_000

    reader = pd.read_csv(
        'transactions.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        dtype={'category': str},
        keep_default_na=False,
        chunksize=chunksize,
    )

    for chunk in reader:
        filtered = chunk[(chunk['account_id'] % 11) < 7]
        if filtered.empty:
            continue

        multiplier = (filtered['account_id'] % 97) + 1

        # Use arbitrary-precision objects if values could overflow 64-bit integers
        max_abs = filtered['amount_cents'].abs().max()
        if max_abs > 90_000_000_000_000:
            val = filtered['amount_cents'].astype(object) * multiplier.astype(object)
        else:
            val = filtered['amount_cents'] * multiplier

        chunk_grouped = val.groupby(filtered['category']).sum()
        for cat, s in chunk_grouped.items():
            totals[cat] = totals.get(cat, 0) + int(s)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")

if __name__ == '__main__':
    main()
