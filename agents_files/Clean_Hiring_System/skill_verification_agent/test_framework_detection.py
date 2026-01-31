"""
Quick test for framework detection on real GitHub repos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.github_api import GitHubAPIClient
from config import GITHUB_PAT

# Initialize client
client = GitHubAPIClient(token=GITHUB_PAT)

# Test with your repo (assuming you have YOLOv8 in one)
test_repos = [
    ("Aadarshsingh16", "convoy-route-mapper-plus"),
]

print("="*60)
print("🧪 Testing Framework Detection")
print("="*60)

for username, repo_name in test_repos:
    full_name = f"{username}/{repo_name}"
    print(f"\n📁 Scanning: {full_name}")
    
    # Get repo info to determine language
    repos = client.get_user_repos(username, max_repos=10)
    repo = next((r for r in repos if r["name"] == repo_name), None)
    
    if not repo:
        print(f"  ❌ Repo not found")
        continue
    
    language = repo.get("language")
    print(f"  Language: {language}")
    
    # Scan for frameworks
    result = client.scan_repo_for_frameworks(full_name, language)
    
    print(f"\n✅ Verified Skills:\n")
    
    # Group by confidence
    high_conf = [d for d in result.get('detections', []) if d['confidence'] == 'high']
    low_conf = [d for d in result.get('detections', []) if d['confidence'] == 'low']
    
    # Display HIGH confidence first
    for detection in high_conf:
        skill = detection['skill']
        evidence_type = detection['evidence_type']
        files = detection.get('files', [])
        
        print(f"🟢 {skill}")
        print(f"   Confidence: HIGH")
        print(f"   Evidence: {evidence_type}")
        if files:
            print(f"   Files:")
            for f in files[:3]:  # Show top 3
                print(f"     - {f}")
        print()
    
    # Display LOW confidence
    for detection in low_conf:
        skill = detection['skill']
        evidence_type = detection['evidence_type']
        reason = detection.get('reason', '')
        files = detection.get('files', [])
        
        print(f"⚠️  {skill}")
        print(f"   Confidence: LOW")
        print(f"   Evidence: {evidence_type}")
        print(f"   Reason: {reason}")
        if files:
            print(f"   Files:")
            for f in files[:3]:  # Show top 3
                print(f"     - {f}")
        print()

print("\n" + "="*60)
print("✅ Test Complete!")
print("="*60)
