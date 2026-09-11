import os
import json
import numpy as np
import pandas as pd

def main():
    df = pd.read_csv(
        'transactions.csv',
        usecols=['account_id', 'category', 'amount_cents'],
        dtype={'account_id': np.int64, 'category': 'category', 'amount_cents': np.int64},
        engine='c'
    )

    aid = df['account_id'].to_numpy()
    mask = (aid % 11) < 7

    aid_m = aid[mask]
    mult = (aid_m % 97) + 1
    amt_m = df['amount_cents'].to_numpy()[mask]
    prod = amt_m * mult

    cat_series = df['category']
    cat_codes = cat_series.cat.codes.to_numpy()[mask]
    categories = cat_series.cat.categories

    unique_codes = np.unique(cat_codes[cat_codes >= 0])
    res = {}
    for code in unique_codes:
        cat_name = str(categories[code])
        res[cat_name] = int(np.sum(prod[cat_codes == code], dtype=np.int64))

    print(f"TOTAL:{json.dumps(res, sort_keys=True)}", flush=True)
    os._exit(0)

if __name__ == '__main__':
    main()
