import asyncio
import httpx
import sys
import os

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Agent URLs from orchestrator (defaults)
AGENTS = {
    "SKILL": "http://localhost:8001",
    "BIAS": "http://localhost:8002",
    "MATCHING": "http://localhost:8003",
    "ATS": "http://localhost:8004",
    "GITHUB": "http://localhost:8005",
    "LEETCODE": "http://localhost:8006",
    "CODEFORCES": "http://localhost:8007",
    "LINKEDIN": "http://localhost:8008",
    "TEST": "http://localhost:8009",
    "PASSPORT": "http://localhost:8010",
}

async def check_health(name, url):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{url}/health")
            if resp.status_code == 200:
                print(f"[OK] {name} is healthy: {resp.json()}")
                return True
            else:
                print(f"[FAIL] {name} health check returned {resp.status_code}")
                return False
    except Exception as e:
        print(f"[FAIL] {name} is unreachable at {url}: {str(e)}")
        return False

async def verify_all():
    print("=== PIPELINE CONNECTIVITY VERIFICATION ===\n")
    
    # 1. Check Backend
    print("Checking Backend...")
    backend_ok = await check_health("BACKEND", BACKEND_URL)
    
    # 2. Check Agents
    print("\nChecking Agents...")
    agent_results = []
    for name, url in AGENTS.items():
        res = await check_health(name, url)
        agent_results.append(res)
    
    print("\n=== SUMMARY ===")
    print(f"Backend: {'READY' if backend_ok else 'NOT FOUND'}")
    print(f"Agents: {sum(agent_results)}/10 ONLINE")
    
    if all(agent_results) and backend_ok:
        print("\n[SUCCESS] Infrastructure is fully operational!")
    else:
        print("\n[WARNING] Some services are missing. Ensure all agents are running.")

if __name__ == "__main__":
    asyncio.run(verify_all())
