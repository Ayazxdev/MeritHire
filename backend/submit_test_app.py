
import requests
import os

url = "http://localhost:8000/candidate/apply"
resume_path = r"D:\Hiring\backend\uploads\ANON-1FCEA2335592\26\Udbhaw_Resume (1).pdf"

with open(resume_path, "rb") as f:
    files = {"resume": f}
    data = {
        "job_id": "6",
        "anon_id": "ANON-1FCEA2335592",
        "github": "https://github.com/udbhaw08"
    }
    
    print("Submitting application...")
    response = requests.post(url, data=data, files=files)
    
if response.status_code == 200:
    print("Success!")
    print(response.json())
else:
    print(f"Failed: {response.status_code}")
    print(response.text)
