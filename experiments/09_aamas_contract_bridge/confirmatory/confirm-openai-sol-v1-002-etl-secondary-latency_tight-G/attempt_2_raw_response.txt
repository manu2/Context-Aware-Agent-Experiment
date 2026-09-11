import json
import sys

import numpy as np
import pandas as pd


def main() -> None:
    totals: dict[str, int] = {}
    int64_max = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "category",
            "amount_cents": "int64",
        },
        chunksize=1_000_000,
        engine="c",
        memory_map=True,
        na_filter=False,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = accounts % 13 < 8
        count = int(mask.sum())
        if count == 0:
            continue

        selected_accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        category_column = chunk["category"]
        codes = category_column.cat.codes.to_numpy(copy=False)[mask]
        categories = category_column.cat.categories

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs_amount = max(abs(minimum), abs(maximum))

        if max_abs_amount <= int64_max // (91 * count):
            weighted = amounts * (selected_accounts % 89 + 3)
            subtotals = pd.Series(weighted, copy=False).groupby(
                codes, sort=False
            ).sum()

            for code, subtotal in subtotals.items():
                key = str(categories[int(code)])
                totals[key] = totals.get(key, 0) + int(subtotal)
        else:
            for code, account, amount in zip(codes, selected_accounts, amounts):
                key = str(categories[int(code)])
                value = int(amount) * (int(account) % 89 + 3)
                totals[key] = totals.get(key, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
