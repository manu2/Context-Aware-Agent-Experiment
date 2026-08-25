import csv
from collections import defaultdict


def process_csv(filename="data.csv"):
    category_sums = defaultdict(float)

    with open(filename, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category_id = row["category_id"]
            metric_val = float(row["metric_val"])
            category_sums[category_id] += metric_val

    # Calculate total count of unique categories
    total_categories = len(category_sums)

    # Output the total count in the specified format
    print(f"TOTAL_CATEGORIES:{total_categories}")


if __name__ == "__main__":
    process_csv()