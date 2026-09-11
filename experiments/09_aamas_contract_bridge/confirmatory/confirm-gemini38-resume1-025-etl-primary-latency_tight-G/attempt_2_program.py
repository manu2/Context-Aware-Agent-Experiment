import json
from collections import defaultdict
import pandas as pd
import numpy as np

def main():
    totals = defaultdict(int)
    chunksize = 500_000

    for chunk in pd.read_csv('transactions.csv', chunksize=chunksize):
        acc = chunk['account_id']
        mask = (acc % 11) < 7
        if not mask.any():
            continue

        sub = chunk.loc[mask]
        mult = (sub['account_id'] % 97) + 1
        amt = sub['amount_cents']

        amt_min = int(amt.min())
        amt_max = int(amt.max())
        max_abs_amt = max(abs(amt_min), abs(amt_max))

        # Check if int64 could overflow during multiplication or chunk sum
        if max_abs_amt * 97 * len(sub) > 8_000_000_000_000_000_000 or amt.dtype == object:
            val = amt.astype(object) * mult.astype(object)
            grouped = val.groupby(sub['category']).sum()
        else:
            val = amt * mult
            grouped = val.groupby(sub['category']).sum()

        for cat, s in grouped.items():
            totals[str(cat)] += int(s)

    print("TOTAL:" + json.dumps(totals, sort_keys=True))

if __name__ == '__main__':
    main()
