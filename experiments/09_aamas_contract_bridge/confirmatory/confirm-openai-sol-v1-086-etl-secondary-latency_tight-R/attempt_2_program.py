import csv
import json

import numpy as np
import pandas as pd


FILE_NAME = "transactions_secondary.csv"
CHUNK_SIZE = 1_000_000
INT64_MAX = (1 << 63) - 1


def compute_with_pandas():
    totals = {}

    reader = pd.read_csv(
        FILE_NAME,
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": np.int64,
            "category": str,
            "amount_cents": np.int64,
        },
        na_filter=False,
        chunksize=CHUNK_SIZE,
        engine="c",
        memory_map=True,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(accounts, 13) < 8
        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].to_numpy(copy=False)[mask]
        multipliers = np.remainder(selected_accounts, 89) + 3

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_absolute_amount = max(abs(minimum), abs(maximum))
        safe_vector_sum = max_absolute_amount * 91 * len(amounts) <= INT64_MAX

        if safe_vector_sum:
            products = amounts * multipliers
            grouped = pd.Series(products, copy=False).groupby(
                categories, sort=False
            ).sum()
            for category, subtotal in grouped.items():
                totals[category] = totals.get(category, 0) + int(subtotal)
        else:
            for category, amount, multiplier in zip(
                categories, amounts, multipliers
            ):
                totals[category] = totals.get(category, 0) + (
                    int(amount) * int(multiplier)
                )

    return totals


def compute_with_csv():
    totals = {}
    with open(FILE_NAME, "r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            account_id = int(row["account_id"])
            if account_id % 13 < 8:
                category = row["category"]
                value = int(row["amount_cents"]) * (account_id % 89 + 3)
                totals[category] = totals.get(category, 0) + value
    return totals


def main():
    try:
        totals = compute_with_pandas()
    except (ValueError, OverflowError):
        totals = compute_with_csv()

    print(
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
