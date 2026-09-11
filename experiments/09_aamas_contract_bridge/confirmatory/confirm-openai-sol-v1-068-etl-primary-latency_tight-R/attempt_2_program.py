import csv
import json
import sys

import numpy as np
import pandas as pd


FILE_NAME = "transactions.csv"
CHUNK_SIZE = 1_000_000
INT64_MAX = np.iinfo(np.int64).max


def add_total(totals, category, value):
    totals[category] = totals.get(category, 0) + int(value)


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
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(accounts, 11) < 7

        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        selected_amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        selected_categories = chunk["category"].to_numpy(copy=False)[mask]

        minimum = int(selected_amounts.min())
        maximum = int(selected_amounts.max())
        max_absolute_amount = max(abs(minimum), abs(maximum))

        safe_for_int64_aggregation = (
            max_absolute_amount * 97 * selected_amounts.size <= INT64_MAX
        )

        if safe_for_int64_aggregation:
            products = selected_amounts * (
                np.remainder(selected_accounts, 97) + 1
            )
            grouped = pd.Series(products, copy=False).groupby(
                selected_categories, sort=False
            ).sum()

            for category, value in grouped.items():
                add_total(totals, category, value)
        else:
            for category, account, amount in zip(
                selected_categories, selected_accounts, selected_amounts
            ):
                value = int(amount) * ((int(account) % 97) + 1)
                add_total(totals, category, value)

    return totals


def compute_with_csv():
    totals = {}

    with open(FILE_NAME, "r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            account = int(row["account_id"])
            if account % 11 < 7:
                value = int(row["amount_cents"]) * ((account % 97) + 1)
                add_total(totals, row["category"], value)

    return totals


try:
    result = compute_with_pandas()
except (ValueError, TypeError, OverflowError, pd.errors.ParserError):
    result = compute_with_csv()

sys.stdout.write(
    "TOTAL:"
    + json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
)
