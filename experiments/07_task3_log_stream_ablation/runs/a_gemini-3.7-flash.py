import sys
from collections import Counter

def process_logs(file_path='server_logs.txt'):
    server_errors = 0
    endpoint_counts = Counter()
    unique_ips = set()

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 7:
                    continue
                
                ip = parts[1]
                endpoint = parts[3]
                status_str = parts[4]
                
                try:
                    status = int(status_str)
                    if 500 <= status < 600:
                        server_errors += 1
                except ValueError:
                    pass
                
                endpoint_counts[endpoint] += 1
                unique_ips.add(ip)
    except FileNotFoundError:
        pass

    top_5 = [ep for ep, _ in endpoint_counts.most_common(5)]
    top_endpoints_str = ",".join(top_5)

    print(f"ERRORS:{server_errors}")
    print(f"TOP_ENDPOINTS:{top_endpoints_str}")
    print(f"UNIQUE_IPS:{len(unique_ips)}")

if __name__ == '__main__':
    process_logs()
