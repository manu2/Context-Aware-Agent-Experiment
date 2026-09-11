import csv
import json
import sys


def main():
    category_sums = {}

    with open("transactions.csv", mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("TOTAL:{}")
            return

        header = [col.strip().lstrip("\ufeff") for col in header]
        cat_idx = header.index("category")
        amt_idx = header.index("amount_cents")

        for row in reader:
            if not row:
                continue
            cat = row[cat_idx]
            amt = int(row[amt_idx])
            category_sums[cat] = category_sums.get(cat, 0) + amt

    json_output = json.dumps(category_sums, sort_keys=True)
    sys.stdout.write(f"TOTAL:{json_output}\n")


if __name__ == "__main__":
    main()
