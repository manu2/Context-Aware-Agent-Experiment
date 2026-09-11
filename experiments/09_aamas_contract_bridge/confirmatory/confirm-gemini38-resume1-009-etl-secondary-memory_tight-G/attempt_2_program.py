import json
import warnings
import pandas as pd

warnings.filterwarnings("ignore")


def main():
    totals = {}
    csv_file = "transactions_secondary.csv"
    chunk_size = 250_000

    # Stream the CSV in chunks to maintain low, constant memory footprint
    for chunk in pd.read_csv(
        csv_file,
        chunksize=chunk_size,
        dtype={"account_id": "int64", "category": "str", "amount_cents": "int64"},
        keep_default_na=False,
    ):
        # Filter rows: account_id % 13 < 8
        filtered = chunk[chunk["account_id"] % 13 < 8]
        if filtered.empty:
            continue

        multiplier = (filtered["account_id"] % 89) + 3

        # Protect against int64 overflow for exact sums
        abs_max = filtered["amount_cents"].abs().max()
        if abs_max * 91 * len(filtered) > 9_000_000_000_000_000_000:
            weighted = filtered["amount_cents"].astype(
                object
            ) * multiplier.astype(object)
        else:
            weighted = filtered["amount_cents"] * multiplier

        # Aggregate within chunk and accumulate
        chunk_totals = weighted.groupby(filtered["category"], dropna=False).sum()
        for cat, val in chunk_totals.items():
            totals[cat] = totals.get(cat, 0) + int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
