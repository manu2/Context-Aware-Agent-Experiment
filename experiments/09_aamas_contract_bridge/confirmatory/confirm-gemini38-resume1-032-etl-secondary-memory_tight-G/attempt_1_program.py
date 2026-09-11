import json
from collections import defaultdict
import pandas as pd


def main():
    filename = "transactions_secondary.csv"
    totals = defaultdict(int)

    chunksize = 500_000
    usecols = ["account_id", "category", "amount_cents"]

    for chunk in pd.read_csv(
        filename, usecols=usecols, chunksize=chunksize, keep_default_na=False
    ):
        acc = chunk["account_id"]
        mask = (acc % 13) < 8
        if not mask.any():
            continue

        sub = chunk[mask]
        sub_acc = sub["account_id"]
        sub_amt = sub["amount_cents"]

        min_val = int(sub_amt.min())
        max_val = int(sub_amt.max())
        max_amt = max(abs(min_val), abs(max_val))

        # Check if operations can safely stay in int64 without overflow
        # (weight is at most 88 + 3 = 91)
        if max_amt * 91 * len(sub) < 8 * 10**18:
            weights = (sub_acc % 89) + 3
            vals = sub_amt * weights
            grp = vals.groupby(sub["category"]).sum()
            for cat, val in grp.items():
                totals[str(cat)] += int(val)
        else:
            # Fall back to arbitrary-precision Python integers if numbers are very large
            for cat, amt, a_id in zip(sub["category"], sub_amt, sub_acc):
                totals[str(cat)] += int(amt) * ((int(a_id) % 89) + 3)

    result_json = json.dumps(dict(totals), sort_keys=True)
    print(f"TOTAL:{result_json}")


if __name__ == "__main__":
    main()
