import csv
import json
import sys

import numpy as np
import pandas as pd


PATH = "transactions.csv"
CHUNK_SIZE = 1_500_000
INT64_MAX = np.iinfo(np.int64).max


def add_total(totals, category, value):
    totals[category] = totals.get(category, 0) + int(value)


def process_with_pandas():
    totals = {}

    with pd.read_csv(
        PATH,
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "category",
            "amount_cents": "int64",
        },
        chunksize=CHUNK_SIZE,
        engine="c",
        na_filter=False,
        memory_map=True,
    ) as reader:
        for chunk in reader:
            accounts = chunk["account_id"].to_numpy(copy=False)
            mask = (accounts % 11) < 7
            count = int(mask.sum())
            if count == 0:
                continue

            selected_accounts = accounts[mask]
            amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
            weights = (selected_accounts % 97) + 1

            minimum = int(amounts.min())
            maximum = int(amounts.max())
            max_abs = max(abs(minimum), abs(maximum))

            categories = chunk.loc[mask, "category"]

            if max_abs * 97 * count <= INT64_MAX:
                products = amounts * weights
                values = pd.Series(products, index=categories.index, copy=False)
                grouped = values.groupby(
                    categories, observed=True, sort=False
                ).sum()

                for category, value in grouped.items():
                    add_total(totals, str(category), value)
            else:
                category_values = categories.astype(object).to_numpy(copy=False)
                for category, amount, weight in zip(
                    category_values, amounts, weights
                ):
                    add_total(
                        totals,
                        str(category),
                        int(amount) * int(weight),
                    )

    return totals


def process_with_csv():
    totals = {}

    with open(PATH, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            account = int(row["account_id"])
            if account % 11 < 7:
                value = int(row["amount_cents"]) * ((account % 97) + 1)
                add_total(totals, row["category"], value)

    return totals


def main():
    try:
        totals = process_with_pandas()
    except (ValueError, TypeError, OverflowError):
        totals = process_with_csv()

    output = json.dumps(
        totals,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    sys.stdout.write("TOTAL:" + output + "\n")


if __name__ == "__main__":
    main()
