import json
import pandas as pd
from pandas.errors import EmptyDataError


def main():
    totals = {}

    try:
        reader = pd.read_csv(
            "transactions.csv",
            usecols=["account_id", "category", "amount_cents"],
            dtype={"category": str},
            keep_default_na=False,
            chunksize=250_000,
        )

        for chunk in reader:
            if chunk.empty:
                continue

            # Filter rows where account_id % 11 < 7
            mask = (chunk["account_id"] % 11) < 7
            filtered = chunk[mask]
            if filtered.empty:
                continue

            mult = (filtered["account_id"] % 97) + 1

            min_amt = int(filtered["amount_cents"].min())
            max_amt = int(filtered["amount_cents"].max())
            max_abs = max(abs(min_amt), abs(max_amt))

            # Fast vectorized path if there is no risk of int64 overflow
            if max_abs * 97 * len(filtered) < 9_000_000_000_000_000_000:
                weighted = filtered["amount_cents"] * mult
                chunk_totals = weighted.groupby(filtered["category"]).sum()
                for cat, val in chunk_totals.items():
                    totals[cat] = totals.get(cat, 0) + int(val)
            else:
                # Arbitrary-precision Python int fallback for extraordinarily large numbers
                for cat, amt, m in zip(
                    filtered["category"], filtered["amount_cents"], mult
                ):
                    totals[cat] = totals.get(cat, 0) + int(amt) * int(m)

    except EmptyDataError:
        pass

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
