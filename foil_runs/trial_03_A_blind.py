import csv
from collections import defaultdict


def process_csv(filename):
    category_sums = defaultdict(float)

    with open(filename, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category_id = row["category_id"]
            metric_val = float(row["metric_val"])
            category_sums[category_id] += metric_val

    # Count unique categories
    total_categories = len(category_sums)

    # Print the requested output format
    print(f"TOTAL_CATEGORIES:{total_categories}")


if __name__ == "__main__":
    process_csv("data.csv")