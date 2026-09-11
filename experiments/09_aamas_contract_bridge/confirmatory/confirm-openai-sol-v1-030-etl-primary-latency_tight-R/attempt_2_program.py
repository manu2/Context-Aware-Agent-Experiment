import csv
import json
import sys

import numpy as np
import pandas as pd


CHUNK_SIZE = 500_000
BASE = 1 << 27


def fast_totals(path):
    totals = {}

    reader = pd.read_csv(
        path,
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "str",
            "amount_cents": "int64",
        },
        keep_default_na=False,
        encoding="utf-8-sig",
        chunksize=CHUNK_SIZE,
    )

    for chunk in reader:
        account_ids = chunk["account_id"].to_numpy(dtype=np.int64, copy=False)
        mask = np.remainder(account_ids, 11) < 7
        if not np.any(mask):
            continue

        selected_ids = account_ids[mask]
        amounts = chunk.loc[mask, "amount_cents"].to_numpy(
            dtype=np.int64, copy=False
        )
        categories = chunk.loc[mask, "category"].to_numpy(copy=False)
        weights = np.remainder(selected_ids, 97) + 1

        high = np.floor_divide(amounts, BASE)
        low = np.remainder(amounts, BASE)

        grouped = pd.DataFrame(
            {
                "category": categories,
                "high": high * weights,
                "low": low * weights,
            }
        ).groupby("category", sort=False, observed=True)[["high", "low"]].sum()

        for category, high_sum, low_sum in grouped.itertuples(
            index=True, name=None
        ):
            value = int(high_sum) * BASE + int(low_sum)
            totals[category] = totals.get(category, 0) + value

    return totals


def fallback_totals(path):
    totals = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            account_id = int(row["account_id"])
            if account_id % 11 < 7:
                category = row["category"]
                value = int(row["amount_cents"]) * ((account_id % 97) + 1)
                totals[category] = totals.get(category, 0) + value
    return totals


def main():
    path = "transactions.csv"
    try:
        totals = fast_totals(path)
    except (ValueError, OverflowError):
        totals = fallback_totals(path)

    sys.stdout.write(
        "TOTAL:"
        + json.dumps(
            totals,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
