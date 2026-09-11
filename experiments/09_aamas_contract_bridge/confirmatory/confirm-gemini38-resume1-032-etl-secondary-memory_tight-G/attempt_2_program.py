import json
import pandas as pd


def main():
    filename = "transactions_secondary.csv"
    totals = {}

    chunksize = 500_000
    dtypes = {
        "account_id": "int64",
        "category": "str",
        "amount_cents": "int64",
    }

    # Process in chunks to maintain low memory usage and avoid OOM
    for chunk in pd.read_csv(
        filename,
        chunksize=chunksize,
        dtype=dtypes,
        keep_default_na=False,
    ):
        mask = (chunk["account_id"] % 13) < 8
        filtered = chunk[mask]
        if filtered.empty:
            continue

        weights = (filtered["account_id"] % 89) + 3

        # Guard against potential 64-bit integer overflow during multiplication/sum
        max_abs = filtered["amount_cents"].abs().max()
        if max_abs * 92 * len(filtered) >= 9_000_000_000_000_000_000:
            term = filtered["amount_cents"].astype(object) * weights.astype(
                object
            )
        else:
            term = filtered["amount_cents"] * weights

        filtered = filtered.assign(_term=term)
        grp = filtered.groupby("category")["_term"].sum()

        for cat, val in grp.items():
            totals[cat] = totals.get(cat, 0) + int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
