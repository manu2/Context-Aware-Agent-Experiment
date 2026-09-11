import json
import sys

import numpy as np
import pandas as pd


def main():
    totals = {}
    int64_max = np.iinfo(np.int64).max
    chunk_size = 1_000_000

    reader = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": str,
            "amount_cents": "int64",
        },
        keep_default_na=False,
        chunksize=chunk_size,
        engine="c",
        memory_map=True,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = (accounts % 11) < 7
        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        selected_amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        selected_categories = chunk["category"].to_numpy(copy=False)[mask]
        count = selected_accounts.size

        minimum = int(selected_amounts.min())
        maximum = int(selected_amounts.max())
        max_abs_amount = max(abs(minimum), abs(maximum))

        if max_abs_amount == 0:
            continue

        if max_abs_amount <= int64_max // 97:
            safe_block_size = int64_max // (max_abs_amount * 97)

            if safe_block_size >= 1000:
                for start in range(0, count, safe_block_size):
                    end = min(start + safe_block_size, count)
                    block_accounts = selected_accounts[start:end]
                    block_amounts = selected_amounts[start:end]
                    block_categories = selected_categories[start:end]

                    products = block_amounts * ((block_accounts % 97) + 1)
                    grouped = pd.Series(products, copy=False).groupby(
                        block_categories, sort=False
                    ).sum()

                    for category, value in grouped.items():
                        totals[category] = totals.get(category, 0) + int(value)
                continue

        for category, account, amount in zip(
            selected_categories, selected_accounts, selected_amounts
        ):
            value = int(amount) * ((int(account) % 97) + 1)
            totals[category] = totals.get(category, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
