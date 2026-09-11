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
            "account_id": np.int64,
            "category": str,
            "amount_cents": np.int64,
        },
        keep_default_na=False,
        na_filter=False,
        chunksize=1_000_000,
        memory_map=True,
    )

    for chunk in reader:
        account_ids = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(account_ids, 13) < 8
        if not mask.any():
            continue

        selected_ids = account_ids[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].to_numpy(copy=False)[mask]
        weights = np.remainder(selected_ids, 89) + 3

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs_amount = max(abs(minimum), abs(maximum))

        if max_abs_amount <= int64_max // 91:
            weighted = amounts * weights
            weighted_min = int(weighted.min())
            weighted_max = int(weighted.max())
            max_abs_weighted = max(abs(weighted_min), abs(weighted_max))

            if max_abs_weighted == 0 or len(weighted) <= int64_max // max_abs_weighted:
                grouped = pd.Series(weighted, copy=False).groupby(
                    categories, sort=False
                ).sum()
                for category, value in grouped.items():
                    totals[category] = totals.get(category, 0) + int(value)
                continue

        for category, account_id, amount in zip(
            categories, selected_ids, amounts
        ):
            value = int(amount) * ((int(account_id) % 89) + 3)
            totals[category] = totals.get(category, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
