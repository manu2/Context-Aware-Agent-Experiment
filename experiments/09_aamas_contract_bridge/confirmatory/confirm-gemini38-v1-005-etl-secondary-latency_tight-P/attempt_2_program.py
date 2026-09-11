import json
import os
import sys
import numpy as np
import pandas as pd


def main():
    # Reading account_id and amount_cents as int64 and category as categorical
    # avoids allocating millions of Python string objects and cuts parsing time by >2x.
    df = pd.read_csv(
        "transactions_secondary.csv",
        engine="c",
        dtype={
            "account_id": np.int64,
            "category": "category",
            "amount_cents": np.int64,
        },
    )

    acc = df["account_id"].to_numpy()
    mask = (acc % 13) < 8

    if not np.any(mask):
        sys.stdout.write("TOTAL:{}\n")
        sys.stdout.flush()
        os._exit(0)

    acc_filt = acc[mask]
    mult = (acc_filt % 89) + 3
    cents = df["amount_cents"].to_numpy()[mask]
    val = cents * mult

    cat_col = df["category"]
    codes = cat_col.cat.codes.to_numpy()[mask]
    categories = cat_col.cat.categories

    totals = {}
    unique_codes = np.unique(codes)
    if len(unique_codes) <= 256:
        for code in unique_codes:
            if code >= 0:
                totals[str(categories[code])] = int(np.sum(val[codes == code]))
    else:
        grouped = pd.Series(val).groupby(codes, sort=False).sum()
        for code, total in grouped.items():
            if code >= 0:
                totals[str(categories[code])] = int(total)

    sys.stdout.write("TOTAL:" + json.dumps(totals, sort_keys=True) + "\n")
    sys.stdout.flush()
    # Immediate exit avoids Python runtime garbage collection overhead of large arrays
    os._exit(0)


if __name__ == "__main__":
    main()
