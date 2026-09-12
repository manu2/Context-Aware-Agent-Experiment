import json
import sys

PATH = "transactions_secondary.csv"
CHUNK_SIZE = 8 * 1024 * 1024


class FastPathUnsupported(Exception):
    pass


def fast_parse():
    totals = {}

    with open(PATH, "rb", buffering=CHUNK_SIZE) as f:
        header = f.readline().rstrip(b"\r\n")
        if header != b"account_id,category,amount_cents":
            raise FastPathUnsupported

        carry = b""
        while True:
            chunk = f.read(CHUNK_SIZE)
            if chunk:
                parts = (carry + chunk).split(b"\n")
                carry = parts.pop()
            else:
                parts = [carry] if carry else []

            get_total = totals.get
            for line in parts:
                first = line.find(b",")
                if first <= 0:
                    raise FastPathUnsupported

                try:
                    account_id = int(line[:first])
                except ValueError:
                    raise FastPathUnsupported from None

                if account_id % 13 >= 8:
                    continue

                last = line.rfind(b",")
                if last <= first:
                    raise FastPathUnsupported

                category = line[first + 1:last]
                if len(category) >= 2 and category[0] == 34 and category[-1] == 34:
                    category = category[1:-1].replace(b'""', b'"')

                try:
                    amount = int(line[last + 1:])
                except ValueError:
                    raise FastPathUnsupported from None

                value = amount * ((account_id % 89) + 3)
                totals[category] = get_total(category, 0) + value

            if not chunk:
                break

    try:
        return {key.decode("utf-8"): value for key, value in totals.items()}
    except UnicodeDecodeError:
        raise FastPathUnsupported from None


def csv_parse():
    import csv

    totals = {}
    with open(PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or not {
            "account_id", "category", "amount_cents"
        }.issubset(reader.fieldnames):
            raise ValueError("Required CSV columns are missing")

        for row in reader:
            account_id = int(row["account_id"])
            if account_id % 13 < 8:
                category = row["category"]
                value = int(row["amount_cents"]) * ((account_id % 89) + 3)
                totals[category] = totals.get(category, 0) + value

    return totals


try:
    result = fast_parse()
except FastPathUnsupported:
    result = csv_parse()

sys.stdout.write(
    "TOTAL:" + json.dumps(result, sort_keys=True, separators=(",", ":"))
)
