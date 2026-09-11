import json
import sys

import numpy as np
import pandas as pd


def main():
    totals = {}
    limit = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "str",
            "amount_cents": "int64",
        },
        keep_default_na=False,
        chunksize=1_000_000,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = (accounts % 11) < 7
        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].to_numpy(copy=False)[mask]
        count = amounts.size

        low = int(amounts.min())
        high = int(amounts.max())
        max_abs_amount = max(abs(low), abs(high))

        if max_abs_amount * 97 * count <= limit:
            products = amounts * ((selected_accounts % 97) + 1)
            codes, unique_categories = pd.factorize(categories, sort=False)
            sums = np.zeros(len(unique_categories), dtype=np.int64)
            np.add.at(sums, codes, products)

            for category, subtotal in zip(unique_categories, sums):
                key = str(category)
                totals[key] = totals.get(key, 0) + int(subtotal)
        else:
            for category, account, amount in zip(
                categories, selected_accounts, amounts
            ):
                key = str(category)
                value = int(amount) * ((int(account) % 97) + 1)
                totals[key] = totals.get(key, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
