import re
import os
import glob

log_dir = r"d:\Hiring\agents_services"
patterns = ["tunnel*.log", "tunnel*.txt"]

latest_url = None
latest_time = 0

for pattern in patterns:
    for log_file in glob.glob(os.path.join(log_dir, pattern)):
        mtime = os.path.getmtime(log_file)
        if mtime > latest_time:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                urls = re.findall(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', content)
                if urls:
                    latest_url = urls[-1]
                    latest_time = mtime

if latest_url:
    print(f"LATEST_URL: {latest_url}")
else:
    print("NO_URL_FOUND")
