import sys
import json
from collections import defaultdict
import numpy as np
import pandas as pd

def main():
    totals = defaultdict(int)
    chunk_size = 500_000

    # Stream in chunks to maintain low memory usage and avoid swapping/OOM
    reader = pd.read_csv(
        'transactions.csv',
        chunksize=chunk_size,
        engine='c',
        dtype={'account_id': np.int64, 'amount_cents': np.int64},
    )

    for chunk in reader:
        acc = chunk['account_id'].to_numpy()
        mask = (acc % 11) < 7
        if not np.any(mask):
            continue

        filtered_chunk = chunk[mask]
        acc_filtered = acc[mask]
        weights = (acc_filtered % 97) + 1
        amt_filtered = filtered_chunk['amount_cents'].to_numpy()

        # Guard against potential int64 overflow when computing weighted amounts
        max_amt = np.max(np.abs(amt_filtered)) if len(amt_filtered) > 0 else 0
        if max_amt > 100_000_000_000:
            weighted = amt_filtered.astype(object) * weights.astype(object)
        else:
            weighted = amt_filtered * weights

        filtered_chunk = filtered_chunk.assign(weighted=weighted)
        grp = filtered_chunk.groupby('category', observed=True)['weighted'].sum()

        for cat, val in grp.items():
            totals[str(cat)] += int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")

if __name__ == '__main__':
    main()
