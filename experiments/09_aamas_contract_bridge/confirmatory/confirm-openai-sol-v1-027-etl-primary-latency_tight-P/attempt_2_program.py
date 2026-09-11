import csv
import json
import sys

import numpy as np
import pandas as pd


PATH = "transactions.csv"
CHUNK_SIZE = 1_000_000
INT64_MAX = np.iinfo(np.int64).max


def compute_with_pandas():
    totals = {}

    reader = pd.read_csv(
        PATH,
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "category",
            "amount_cents": "int64",
        },
        na_filter=False,
        chunksize=CHUNK_SIZE,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        selected = accounts % 11 < 7
        if not selected.any():
            continue

        accounts = accounts[selected]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[selected]
        codes = chunk["category"].cat.codes.to_numpy(copy=False)[selected]
        categories = chunk["category"].cat.categories

        category_sums = np.zeros(len(categories), dtype=np.int64)
        used = np.zeros(len(categories), dtype=bool)
        used[codes] = True

        bound = INT64_MAX // (97 * len(amounts))
        unsafe = (amounts > bound) | (amounts < -bound)

        if unsafe.any():
            safe = ~unsafe
            if safe.any():
                products = amounts[safe] * ((accounts[safe] % 97) + 1)
                np.add.at(category_sums, codes[safe], products)

            for code, account, amount in zip(
                codes[unsafe], accounts[unsafe], amounts[unsafe]
            ):
                key = str(categories[int(code)])
                totals[key] = totals.get(key, 0) + int(amount) * (
                    (int(account) % 97) + 1
                )
        else:
            products = amounts * ((accounts % 97) + 1)
            np.add.at(category_sums, codes, products)

        for code in np.flatnonzero(used):
            key = str(categories[int(code)])
            totals[key] = totals.get(key, 0) + int(category_sums[code])

    return totals


def compute_fallback():
    totals = {}
    with open(PATH, "r", encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            account = int(row["account_id"])
            if account % 11 < 7:
                key = row["category"]
                value = int(row["amount_cents"]) * ((account % 97) + 1)
                totals[key] = totals.get(key, 0) + value
    return totals


try:
    result = compute_with_pandas()
except (ValueError, OverflowError):
    result = compute_fallback()

sys.stdout.write(
    "TOTAL:" + json.dumps(result, sort_keys=True, separators=(",", ":"))
)
