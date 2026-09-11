import json
import pandas as pd

def main():
    totals = {}
    chunk_size = 250_000

    try:
        reader = pd.read_csv(
            'transactions.csv',
            chunksize=chunk_size,
            usecols=['account_id', 'category', 'amount_cents'],
            dtype={'account_id': 'int64', 'category': 'str', 'amount_cents': 'int64'},
            keep_default_na=False,
        )

        for chunk in reader:
            filtered = chunk[(chunk['account_id'] % 11) < 7]
            if filtered.empty:
                continue

            multiplier = (filtered['account_id'] % 97) + 1
            weighted_amount = filtered['amount_cents'] * multiplier
            chunk_totals = weighted_amount.groupby(filtered['category']).sum()

            for category, total in chunk_totals.items():
                totals[category] = totals.get(category, 0) + int(total)

    except FileNotFoundError:
        pass

    json_str = json.dumps(totals, sort_keys=True)
    print(f"TOTAL:{json_str}")

if __name__ == '__main__':
    main()
