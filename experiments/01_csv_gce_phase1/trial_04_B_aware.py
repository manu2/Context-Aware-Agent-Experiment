import csv
import sys


def process_csv(filename="data.csv"):
    category_sums = {}

    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)

            # Read header and locate required column indices
            header = next(reader, None)
            if not header:
                print("TOTAL_CATEGORIES:0")
                return

            try:
                cat_idx = header.index("category_id")
                metric_idx = header.index("metric_val")
            except ValueError as e:
                print(
                    f"Error: Required column missing from CSV header ({e})",
                    file=sys.stderr,
                )
                print("TOTAL_CATEGORIES:0")
                return

            # Stream through rows to conserve memory
            max_idx = max(cat_idx, metric_idx)
            for row in reader:
                if len(row) <= max_idx:
                    continue

                cat_id = row[cat_idx]
                try:
                    metric_val = float(row[metric_idx])
                except ValueError:
                    # Skip rows with non-numeric metric values
                    continue

                category_sums[cat_id] = (
                    category_sums.get(cat_id, 0.0) + metric_val
                )

        print(f"TOTAL_CATEGORIES:{len(category_sums)}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        print("TOTAL_CATEGORIES:0")


if __name__ == "__main__":
    process_csv()