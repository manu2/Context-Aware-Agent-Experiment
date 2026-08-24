import csv
from collections import defaultdict


def main():
    csv_file = "data.csv"
    category_sums = defaultdict(float)

    with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category_id = row["category_id"]
            metric_val = float(row["metric_val"]) if row["metric_val"] else 0.0
            category_sums[category_id] += metric_val

    # Print the total count of unique categories
    print(f"TOTAL_CATEGORIES:{len(category_sums)}")


if __name__ == "__main__":
    main()