import subprocess
import re
import time
import sys

def start_tunnel():
    print("Starting Cloudflare Tunnel...")
    proc = subprocess.Popen(
        ["npx.cmd", "cloudflared", "tunnel", "--url", "http://localhost:8011"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )

    url = None
    start_time = time.time()
    
    # Wait up to 30 seconds for the URL
    while time.time() - start_time < 30:
        line = proc.stdout.readline()
        if not line:
            break
        print(f"LOG: {line.strip()}")
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if match:
            url = match.group(0)
            with open("tunnel_url.txt", "w") as f:
                f.write(url)
            print("\n" + "="*60)
            print(f"SUCCESS! Your tunnel URL is: {url}")
            print(f"Use this in ArmorIQ: {url}/mcp")
            print("="*60 + "\n")
            # Don't exit, keep the tunnel running!
            
    if not url:
        print("Failed to find tunnel URL in time.")
    
    # Keep the process alive
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()

if __name__ == "__main__":
    start_tunnel()
