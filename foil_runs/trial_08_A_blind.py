import csv
from collections import defaultdict


def process_csv(file_path="data.csv"):
    category_sums = defaultdict(float)

    with open(file_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            category_id = row["category_id"]
            try:
                metric_val = float(row["metric_val"])
            except (ValueError, TypeError):
                metric_val = 0.0

            # Group and accumulate the sum
            category_sums[category_id] += metric_val

    # Print the final total count of unique categories
    total_categories = len(category_sums)
    print(f"TOTAL_CATEGORIES:{total_categories}")


if __name__ == "__main__":
    process_csv("data.csv")