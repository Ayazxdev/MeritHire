import requests
import json

url = "http://localhost:8011/mcp"
headers = {
    "Content-Type": "application/json",
    "x-api-key": "fh_mcp_sk_dev_default_secret"
}

payload = {
    "jsonrpc": "2.0", 
    "id": 1, 
    "method": "tools/call", 
    "params": {
        "name": "bias_audit", 
        "arguments": {
            "credential_json": "{}", 
            "metadata_json": "{}"
        }
    }
}

try:
    print(f"Testing MCP Tool: bias_audit at {url}")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
