import csv
import sys


def process_csv(file_path="data.csv"):
    category_sums = {}

    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)

            if not header:
                print("TOTAL_CATEGORIES:0")
                return

            # Find column indices for 'category_id' and 'metric_val'
            cat_idx = header.index("category_id")
            val_idx = header.index("metric_val")

            for row in reader:
                if len(row) > max(cat_idx, val_idx):
                    cat_id = row[cat_idx]
                    try:
                        val = float(row[val_idx])
                    except ValueError:
                        # Skip rows where metric_val is not a valid number
                        continue

                    category_sums[cat_id] = (
                        category_sums.get(cat_id, 0.0) + val
                    )

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        return
    except KeyError as e:
        print(f"Error: Missing required column {e}", file=sys.stderr)
        return

    # Output the total count of unique categories
    print(f"TOTAL_CATEGORIES:{len(category_sums)}")


if __name__ == "__main__":
    process_csv()