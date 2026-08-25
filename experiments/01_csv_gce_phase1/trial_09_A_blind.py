import csv
from collections import defaultdict


def process_data(file_path="data.csv"):
    category_totals = defaultdict(float)

    with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            category_id = row["category_id"]
            try:
                metric_val = float(row["metric_val"])
            except (ValueError, TypeError):
                metric_val = 0.0

            category_totals[category_id] += metric_val

    # Print the total count of unique categories
    total_unique_categories = len(category_totals)
    print(f"TOTAL_CATEGORIES:{total_unique_categories}")


if __name__ == "__main__":
    process_data()