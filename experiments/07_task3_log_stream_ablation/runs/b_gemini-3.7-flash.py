import sys
from collections import Counter

def process_logs(filepath: str = "server_logs.txt") -> None:
    error_5xx_count = 0
    endpoint_counts = Counter()
    unique_ips = set()

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue

                ip = parts[1]
                endpoint = parts[3]
                status_code = parts[4]

                unique_ips.add(ip)
                endpoint_counts[endpoint] += 1

                try:
                    code = int(status_code)
                    if 500 <= code < 600:
                        error_5xx_count += 1
                except ValueError:
                    pass
    except FileNotFoundError:
        pass

    top_5_endpoints = [ep for ep, _ in endpoint_counts.most_common(5)]
    top_endpoints_str = ",".join(top_5_endpoints)

    print(f"ERRORS:{error_5xx_count}")
    print(f"TOP_ENDPOINTS:{top_endpoints_str}")
    print(f"UNIQUE_IPS:{len(unique_ips)}")

if __name__ == "__main__":
    process_logs()
