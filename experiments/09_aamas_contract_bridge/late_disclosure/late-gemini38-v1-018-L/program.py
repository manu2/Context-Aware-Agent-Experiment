import sys
import json
from collections import defaultdict
import pandas as pd


def main():
    try:
        df = pd.read_csv("transactions.csv", keep_default_na=False)
    except Exception:
        print("TOTAL:{}")
        return

    if df.empty or "account_id" not in df.columns:
        print("TOTAL:{}")
        return

    # Filter rows whose account_id modulo 11 is less than 7
    mask = (df["account_id"] % 11) < 7
    df = df[mask]

    if df.empty:
        print("TOTAL:{}")
        return

    weights = (df["account_id"] % 97) + 1

    # Exact sum calculation:
    # Check if max possible sum fits safely within signed 64-bit integer limits.
    max_amt = df["amount_cents"].abs().max()
    if max_amt * 98 * len(df) < (1 << 62):
        val = df["amount_cents"] * weights
        grouped = val.groupby(df["category"], observed=True).sum()
        res = {str(k): int(v) for k, v in grouped.items()}
    else:
        # Fall back to arbitrary-precision Python integers
        res = defaultdict(int)
        amt = df["amount_cents"].tolist()
        w_list = weights.tolist()
        cats = df["category"].tolist()
        for c, a, w in zip(cats, amt, w_list):
            res[str(c)] += a * w

    print(f"TOTAL:{json.dumps(res, sort_keys=True)}")


if __name__ == "__main__":
    main()
