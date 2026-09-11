import json
import sys

import numpy as np
import pandas as pd


def main() -> None:
    totals: dict[str, int] = {}
    int64_max = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": "int64", "category": str, "amount_cents": "int64"},
        chunksize=2_000_000,
        keep_default_na=False,
        na_filter=False,
        memory_map=True,
    )

    for chunk in reader:
        account_ids = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(account_ids, 11) < 7
        if not mask.any():
            continue

        selected_ids = account_ids[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].to_numpy(copy=False)[mask]
        weights = np.remainder(selected_ids, 97) + 1

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_absolute = max(abs(minimum), abs(maximum))

        if len(amounts) * max_absolute * 97 <= int64_max:
            products = amounts * weights
            grouped = pd.DataFrame(
                {"category": categories, "value": products},
                copy=False,
            ).groupby("category", sort=False, observed=True)["value"].sum()

            for category, subtotal in grouped.items():
                key = str(category)
                totals[key] = totals.get(key, 0) + int(subtotal)
        else:
            for category, amount, weight in zip(categories, amounts, weights):
                key = str(category)
                totals[key] = totals.get(key, 0) + int(amount) * int(weight)

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
