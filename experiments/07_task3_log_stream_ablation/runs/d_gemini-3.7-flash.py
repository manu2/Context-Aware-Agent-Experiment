from collections import Counter
import sys

def process_logs(filename='server_logs.txt'):
    error_5xx_count = 0
    endpoint_counts = Counter()
    unique_ips = set()

    with open(filename, 'r', encoding='utf-8', errors='ignore', buffering=1024 * 1024) as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 5:
                ip = parts[1]
                endpoint = parts[3]
                status = parts[4]

                unique_ips.add(ip)
                endpoint_counts[endpoint] += 1

                if '500' <= status < '600':
                    error_5xx_count += 1

    top_5_endpoints = [endpoint for endpoint, _ in endpoint_counts.most_common(5)]

    print(f"ERRORS:{error_5xx_count}")
    print(f"TOP_ENDPOINTS:{','.join(top_5_endpoints)}")
    print(f"UNIQUE_IPS:{len(unique_ips)}")

if __name__ == '__main__':
    log_file = sys.argv[1] if len(sys.argv) > 1 else 'server_logs.txt'
    process_logs(log_file)
