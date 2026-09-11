from collections import defaultdict
import json
import pandas as pd


def main():
    totals = defaultdict(int)
    chunksize = 250_000

    for chunk in pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        chunksize=chunksize,
    ):
        acc = chunk["account_id"]
        mask = (acc % 13) < 8
        if not mask.any():
            continue

        filtered = chunk[mask]
        weights = (filtered["account_id"] % 89) + 3
        weighted_amounts = filtered["amount_cents"] * weights

        chunk_sums = weighted_amounts.groupby(filtered["category"]).sum()
        for cat, val in chunk_sums.items():
            totals[cat] += int(val)

    json_output = json.dumps(totals, sort_keys=True)
    print(f"TOTAL:{json_output}")


if __name__ == "__main__":
    main()
