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
            "category": "category",
            "amount_cents": "int64",
        },
        chunksize=100_000,
        engine="c",
        na_filter=False,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        selected = np.remainder(accounts, 11) < 7
        if not selected.any():
            continue

        selected_accounts = accounts[selected]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[selected]
        codes = chunk["category"].cat.codes.to_numpy(copy=False)[selected]
        categories = chunk["category"].cat.categories

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs_amount = max(abs(minimum), abs(maximum))

        if max_abs_amount * 97 * len(amounts) <= limit:
            values = amounts * (np.remainder(selected_accounts, 97) + 1)
            subtotals = np.zeros(len(categories), dtype=np.int64)
            present = np.zeros(len(categories), dtype=np.bool_)
            np.add.at(subtotals, codes, values)
            present[codes] = True

            for code in np.flatnonzero(present):
                category = categories[code]
                totals[category] = totals.get(category, 0) + int(subtotals[code])
        else:
            for account, code, amount in zip(selected_accounts, codes, amounts):
                category = categories[int(code)]
                value = int(amount) * ((int(account) % 97) + 1)
                totals[category] = totals.get(category, 0) + value

    sys.stdout.write(
        "TOTAL:"
        + json.dumps(totals, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    )


if __name__ == "__main__":
    main()
