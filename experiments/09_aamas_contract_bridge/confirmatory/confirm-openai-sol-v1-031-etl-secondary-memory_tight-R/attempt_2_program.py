import json

import numpy as np
import pandas as pd


def main():
    totals = {}
    limit = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "category",
            "amount_cents": "int64",
        },
        keep_default_na=False,
        chunksize=4_000_000,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(accounts, 13) < 8
        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        weights = np.remainder(selected_accounts, 89) + 3
        categories = chunk["category"].array[mask]

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs = max(abs(minimum), abs(maximum))

        if max_abs * 91 * len(amounts) <= limit:
            values = amounts * weights
            grouped = (
                pd.DataFrame({"category": categories, "value": values})
                .groupby("category", observed=True, sort=False)["value"]
                .sum()
            )
            for category, value in grouped.items():
                key = str(category)
                totals[key] = totals.get(key, 0) + int(value)
        else:
            labels = categories.categories
            codes = categories.codes
            for code, amount, weight in zip(codes, amounts, weights):
                if code >= 0:
                    key = str(labels[code])
                    totals[key] = totals.get(key, 0) + int(amount) * int(weight)

    print("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
