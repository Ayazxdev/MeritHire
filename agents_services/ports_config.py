"""
Centralized Port Configuration for All Services

This is the SINGLE SOURCE OF TRUTH for all service ports.
All services and configuration files MUST reference this file.

NEVER hardcode ports anywhere else!
"""

# Agent Service Ports
PORTS = {
    "SKILL": 8001,
    "BIAS": 8002,
    "MATCHING": 8003,
    "ATS": 8004,
    "GITHUB": 8005,
    "LEETCODE": 8006,
    "CODEFORCES": 8007,
    "LINKEDIN": 8008,
    "TEST": 8009,
    "PASSPORT": 8010,  # FIXED: Was 8011, now 8010 to match backend
    "MCP": 8011,       # ArmorIQ MCP Server
}

# Service URLs (for backend and other services)
SERVICE_URLS = {
    name: f"http://localhost:{port}"
    for name, port in PORTS.items()
}

# Health check endpoints
HEALTH_ENDPOINTS = {
    name: f"{url}/health"
    for name, url in SERVICE_URLS.items()
}

# Service file mapping
SERVICE_FILES = {
    "ATS": "ats_service.py",
    "GITHUB": "github_service.py",
    "LEETCODE": "leetcode_service.py",
    "CODEFORCES": "codeforce_service.py",
    "LINKEDIN": "linkedin_service.py",
    "SKILL": "skill_agent_service.py",
    "TEST": "conditional_test_service.py",
    "BIAS": "bias_agent_service.py",
    "MATCHING": "matching_agent_service.py",
    "PASSPORT": "passport_service.py",
    "MCP": "start_mcp.py",
}

# Pipeline stage order
PIPELINE_STAGES = [
    ("ATS", "Stage 1 - ATS Fraud Detection"),
    ("GITHUB", "Stage 2 - GitHub Scraper"),
    ("LEETCODE", "Stage 3 - LeetCode Scraper"),
    ("CODEFORCES", "Stage 4 - Codeforces Scraper"),
    ("LINKEDIN", "Stage 5 - LinkedIn Parser"),
    ("SKILL", "Stage 6 - Skill Verification"),
    ("TEST", "Stage 7 - Conditional Test"),
    ("BIAS", "Stage 8 - Bias Detection"),
    ("MATCHING", "Stage 9 - Job Matching"),
    ("PASSPORT", "Stage 10 - Passport Issuance"),
    ("MCP", "Stage 11 - ArmorIQ MCP Server"),
]


def get_port(service_name: str) -> int:
    """Get port for a service by name"""
    return PORTS.get(service_name.upper())


def get_url(service_name: str) -> str:
    """Get URL for a service by name"""
    return SERVICE_URLS.get(service_name.upper())


def get_health_url(service_name: str) -> str:
    """Get health check URL for a service by name"""
    return HEALTH_ENDPOINTS.get(service_name.upper())
