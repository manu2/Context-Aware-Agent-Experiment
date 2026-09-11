import json
import sys

import numpy as np
import pandas as pd


def main() -> None:
    totals: dict[str, int] = {}

    reader = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": np.int64,
            "category": "category",
            "amount_cents": np.int64,
        },
        engine="c",
        chunksize=2_000_000,
        na_filter=False,
        memory_map=True,
    )

    for chunk in reader:
        account_ids = chunk["account_id"].to_numpy(copy=False)
        selected = np.remainder(account_ids, 13) < 8
        if not selected.any():
            continue

        selected_ids = account_ids[selected]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[selected]
        values = amounts * (np.remainder(selected_ids, 89) + 3)

        category_codes = chunk["category"].cat.codes.to_numpy(copy=False)[selected]
        categories = chunk["category"].cat.categories
        sums = np.zeros(len(categories), dtype=np.int64)
        np.add.at(sums, category_codes, values)

        used_codes = np.unique(category_codes)
        for code in used_codes:
            key = str(categories[int(code)])
            totals[key] = totals.get(key, 0) + int(sums[int(code)])

    sys.stdout.write("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
