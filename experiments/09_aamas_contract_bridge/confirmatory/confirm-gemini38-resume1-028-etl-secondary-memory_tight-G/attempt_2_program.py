import csv
import json
from collections import defaultdict
import numpy as np
import pandas as pd


def main():
    totals = defaultdict(int)
    file_path = "transactions_secondary.csv"

    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)

    col_map = {col.strip(): i for i, col in enumerate(header)}
    acc_col = header[col_map["account_id"]]
    cat_col = header[col_map["category"]]
    amt_col = header[col_map["amount_cents"]]

    usecols = [acc_col, cat_col, amt_col]
    chunksize = 200_000

    for chunk in pd.read_csv(
        file_path,
        usecols=usecols,
        chunksize=chunksize,
        encoding="utf-8-sig",
        keep_default_na=False,
    ):
        if (
            acc_col != "account_id"
            or cat_col != "category"
            or amt_col != "amount_cents"
        ):
            chunk.rename(
                columns={
                    acc_col: "account_id",
                    cat_col: "category",
                    amt_col: "amount_cents",
                },
                inplace=True,
            )

        if not np.issubdtype(chunk["account_id"].dtype, np.integer):
            chunk["account_id"] = pd.to_numeric(chunk["account_id"], errors="coerce")

        mask = (chunk["account_id"] % 13) < 8
        filtered = chunk[mask]
        if filtered.empty:
            continue

        if (
            np.issubdtype(filtered["account_id"].dtype, np.integer)
            and np.issubdtype(filtered["amount_cents"].dtype, np.integer)
            and filtered["amount_cents"].abs().max() <= 10**12
        ):
            mult = (filtered["account_id"] % 89) + 3
            val = filtered["amount_cents"] * mult
            grp = val.groupby(filtered["category"], observed=False).sum()
            for cat, s in grp.items():
                totals[str(cat)] += int(s)
        else:
            for acc, cat, amt in zip(
                filtered["account_id"],
                filtered["category"],
                filtered["amount_cents"],
            ):
                acc_int = int(acc)
                amt_int = int(amt)
                mult = (acc_int % 89) + 3
                totals[str(cat)] += amt_int * mult

    sorted_totals = dict(sorted(totals.items()))
    print(f"TOTAL:{json.dumps(sorted_totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
