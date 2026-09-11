import sys
import json

weights = tuple((i % 97) + 1 if i % 11 < 7 else 0 for i in range(1067))
totals = {}

with open("transactions.csv", "rb", buffering=1024 * 1024) as f:
    header = f.readline().rstrip(b"\r\n")
    if header.startswith(b"\xef\xbb\xbf"):
        header = header[3:]

    if header == b"account_id,category,amount_cents":
        get_total = totals.get
        comma = b","

        for line in f:
            first = line.find(comma)
            if first < 0:
                continue

            weight = weights[int(line[:first]) % 1067]
            if not weight:
                continue

            last = line.rfind(comma)
            category = line[first + 1:last]
            if len(category) >= 2 and category[0] == 34 and category[-1] == 34:
                category = category[1:-1]
                if b'""' in category:
                    category = category.replace(b'""', b'"')

            value = int(line[last + 1:]) * weight
            totals[category] = get_total(category, 0) + value
    else:
        import csv

        f.close()
        with open("transactions.csv", "r", encoding="utf-8-sig", newline="") as text_file:
            reader = csv.DictReader(text_file)
            for row in reader:
                account_id = int(row["account_id"])
                weight = weights[account_id % 1067]
                if weight:
                    category = row["category"].encode("utf-8")
                    totals[category] = totals.get(category, 0) + int(row["amount_cents"]) * weight

result = {key.decode("utf-8"): value for key, value in totals.items()}
sys.stdout.write("TOTAL:" + json.dumps(result, sort_keys=True, separators=(",", ":")))
