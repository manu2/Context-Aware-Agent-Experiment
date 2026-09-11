import json
from collections import defaultdict
import numpy as np
import pandas as pd

def main():
    totals = defaultdict(int)
    
    dtypes = {
        'account_id': np.int64,
        'category': 'str',
        'amount_cents': np.int64
    }
    
    for chunk in pd.read_csv(
        'transactions.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        dtype=dtypes,
        chunksize=500_000
    ):
        mask = (chunk['account_id'] % 11) < 7
        filtered = chunk[mask]
        if filtered.empty:
            continue
        
        multipliers = (filtered['account_id'] % 97) + 1
        weighted_amounts = filtered['amount_cents'] * multipliers
        
        grouped = weighted_amounts.groupby(filtered['category'], sort=False).sum()
        for category, total in grouped.items():
            totals[category] += int(total)
            
    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")

if __name__ == '__main__':
    main()
