import collections
import json
import pandas as pd


def main():
    totals = collections.defaultdict(int)

    # Process in chunks to prevent kernel OOM kill on large files
    for chunk in pd.read_csv('transactions_secondary.csv', chunksize=250000):
        mask = (chunk['account_id'] % 13) < 8
        if not mask.any():
            continue

        filtered = chunk.loc[mask]
        mult = (filtered['account_id'] % 89) + 3

        # Cast to object to ensure exact arbitrary-precision integer arithmetic
        prod = filtered['amount_cents'].astype(object) * mult
        grouped = prod.groupby(filtered['category']).sum()

        for cat, val in grouped.items():
            totals[str(cat)] += int(val)

    # Ensure output is a sorted JSON object
    output = json.dumps(totals, sort_keys=True)
    print(f'TOTAL:{output}')


if __name__ == '__main__':
    main()
