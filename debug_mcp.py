
import requests
import json
import sys

def test_endpoint(url):
    print(f"\n--- Testing {url} ---")
    try:
        resp = requests.get(url, timeout=5)
        print(f"Status: {resp.status_code}")
        print("Headers:", json.dumps(dict(resp.headers), indent=2))
        try:
            print("Body:", json.dumps(resp.json(), indent=2))
        except:
            print("Body (Text):", resp.text[:500])
    except Exception as e:
        print(f"ERROR: {e}")

print("Checking Local MCP Server...")
test_endpoint("http://localhost:8011/")
test_endpoint("http://localhost:8011/mcp")
