import csv
from collections import defaultdict


def process_csv(filename="data.csv"):
    category_totals = defaultdict(float)

    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                category_id = row["category_id"]
                try:
                    metric_val = float(row["metric_val"])
                except (ValueError, TypeError):
                    metric_val = 0.0

                category_totals[category_id] += metric_val

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return

    # Count unique categories and print in the specified format
    total_unique_categories = len(category_totals)
    print(f"TOTAL_CATEGORIES:{total_unique_categories}")


if __name__ == "__main__":
    process_csv("data.csv")