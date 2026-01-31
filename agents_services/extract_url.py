import re
import os

log_files = [r"d:\Hiring\agents_services\tunnel_final.txt", r"d:\Hiring\agents_services\tunnel_debug.txt"]

found = False
for log_file in log_files:
    if not os.path.exists(log_file):
        continue
    
    # Try reading with different encodings
    for encoding in ['utf-16', 'utf-8', 'cp1252']:
        try:
            with open(log_file, 'r', encoding=encoding) as f:
                content = f.read()
                # Look for lines containing trycloudflare.com
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', content)
                if match:
                    print(f"URL_FOUND: {match.group(0)}")
                    found = True
                    break
        except:
            continue
    if found:
        break

if not found:
    print("URL not found in log files.")
    exit(1)
