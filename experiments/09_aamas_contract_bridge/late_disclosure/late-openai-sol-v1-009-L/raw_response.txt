import sys
import json
import csv
import io

def main():
    totals = {}

    with open("transactions_secondary.csv", "rb", buffering=1024 * 1024) as f:
        header = f.readline()
        if header.startswith(b"\xef\xbb\xbf"):
            header = header[3:]

        columns = [c.strip().strip(b'"').decode("utf-8") for c in header.rstrip(b"\r\n").split(b",")]

        if columns == ["account_id", "category", "amount_cents"]:
            for line in f:
                first = line.find(b",")
                last = line.rfind(b",")
                if first < 0 or last == first:
                    continue

                account_id = int(line[:first])
                if account_id % 13 >= 8:
                    continue

                category = line[first + 1:last]
                if len(category) >= 2 and category[0] == 34 and category[-1] == 34:
                    category = category[1:-1].replace(b'""', b'"')

                amount = int(line[last + 1:])
                totals[category] = totals.get(category, 0) + amount * (account_id % 89 + 3)
        else:
            account_index = columns.index("account_id")
            category_index = columns.index("category")
            amount_index = columns.index("amount_cents")

            text_stream = io.TextIOWrapper(f, encoding="utf-8", newline="")
            for row in csv.reader(text_stream):
                account_id = int(row[account_index])
                if account_id % 13 < 8:
                    category = row[category_index].encode("utf-8")
                    amount = int(row[amount_index])
                    totals[category] = totals.get(category, 0) + amount * (account_id % 89 + 3)

    result = {key.decode("utf-8"): value for key, value in totals.items()}
    sys.stdout.write("TOTAL:" + json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False))

if __name__ == "__main__":
    main()
