
import requests
import json

url = "http://localhost:8004/run"
payload = {
    "application_id": 26,
    "resume_text": "Dummy text",
    "resume_path": r"D:\Hiring\backend\uploads\ANON-1FCEA2335592\26\Udbhaw_Resume (1).pdf"
}

try:
    print(f"Calling ATS service at {url}...")
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
