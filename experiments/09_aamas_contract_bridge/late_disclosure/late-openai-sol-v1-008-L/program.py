import json
import sys


def unquote(field):
    if len(field) >= 2 and field[0] == 34 and field[-1] == 34:
        return field[1:-1].replace(b'""', b'"')
    return field


def fallback():
    import csv

    totals = {}
    with open("transactions.csv", "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            account_id = int(row["account_id"])
            if account_id % 11 < 7:
                category = row["category"]
                value = int(row["amount_cents"]) * ((account_id % 97) + 1)
                totals[category] = totals.get(category, 0) + value
    return totals


def main():
    totals = {}

    with open("transactions.csv", "rb") as f:
        header = f.readline().rstrip(b"\r\n")
        if header.startswith(b"\xef\xbb\xbf"):
            header = header[3:]

        if header != b"account_id,category,amount_cents":
            totals = fallback()
        else:
            readline = f.readline
            byte_totals = {}

            while True:
                line = readline()
                if not line:
                    break
                if line in (b"\n", b"\r\n"):
                    continue

                first_comma = line.find(b",")
                if first_comma < 0:
                    continue

                if line[first_comma + 1:first_comma + 2] == b'"':
                    quote_count = line[first_comma + 1:].count(b'"')
                    if quote_count & 1:
                        chunks = [line]
                        while quote_count & 1:
                            continuation = readline()
                            if not continuation:
                                break
                            chunks.append(continuation)
                            quote_count += continuation.count(b'"')
                        line = b"".join(chunks)

                last_comma = line.rfind(b",")
                if last_comma <= first_comma:
                    continue

                account_field = unquote(line[:first_comma])
                account_id = int(account_field)
                if account_id % 11 >= 7:
                    continue

                category = unquote(line[first_comma + 1:last_comma])
                amount = int(unquote(line[last_comma + 1:]))
                value = amount * ((account_id % 97) + 1)
                byte_totals[category] = byte_totals.get(category, 0) + value

            totals = {
                category.decode("utf-8"): value
                for category, value in byte_totals.items()
            }

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
