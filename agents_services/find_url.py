import re
import os

log_files = [
    r"d:\Hiring\agents_services\tunnel_latest.log",
    r"d:\Hiring\agents_services\tunnel_url_live.log",
    r"d:\Hiring\agents_services\tunnel_final.txt"
]

for log_file in log_files:
    if not os.path.exists(log_file):
        continue
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Find all URLs and pick the last one
        urls = re.findall(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', content)
        if urls:
            print(f"File: {log_file} -> {urls[-1]}")
