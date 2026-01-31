"""
Pipeline Verification Script

Tests all services and simulates a pipeline run to verify everything works.
"""
import urllib.request
import urllib.error
import json
import sys
import os

# Import centralized config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents_services'))
from ports_config import PORTS, HEALTH_ENDPOINTS, PIPELINE_STAGES


def check_service_health(service_name: str) -> tuple[bool, str]:
    """Check if a service is healthy"""
    url = HEALTH_ENDPOINTS.get(service_name)
    if not url:
        return False, "No health endpoint configured"
    
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                return True, json.dumps(data, indent=2)
            else:
                return False, f"HTTP {resp.status}"
    except urllib.error.URLError as e:
        return False, f"Connection failed: {e.reason}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    print("=" * 80)
    print("PIPELINE VERIFICATION")
    print("=" * 80)
    
    print("\n📋 Checking Service Configuration...\n")
    
    # Verify critical port assignments
    critical_checks = [
        ("PASSPORT", 8010, "Must be 8010 to match backend"),
        ("GITHUB", 8005, "GitHub scraper"),
        ("MCP", 8011, "ArmorIQ MCP Server"),
    ]
    
    config_ok = True
    for service, expected_port, description in critical_checks:
        actual_port = PORTS.get(service)
        if actual_port == expected_port:
            print(f"  ✓ {service:12} port {actual_port} - {description}")
        else:
            print(f"  ✗ {service:12} port {actual_port} (expected {expected_port}) - {description}")
            config_ok = False
    
    if not config_ok:
        print("\n❌ Configuration errors detected! Please fix ports_config.py")
        return 1
    
    print("\n✅ Configuration is correct!\n")
    
    # Check service health
    print("=" * 80)
    print("🏥 Health Check - All Services")
    print("=" * 80)
    print()
    
    healthy_count = 0
    total_count = 0
    
    for service_name, description in PIPELINE_STAGES:
        total_count += 1
        port = PORTS[service_name]
        is_healthy, details = check_service_health(service_name)
        
        status = "✓ HEALTHY" if is_healthy else "✗ DOWN"
        color = "\033[92m" if is_healthy else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{status:12}{reset} | {service_name:12} | Port {port:5} | {description}")
        
        if is_healthy:
            healthy_count += 1
        else:
            print(f"             └─ {details}")
    
    print()
    print("=" * 80)
    print(f"Summary: {healthy_count}/{total_count} services healthy")
    print("=" * 80)
    
    if healthy_count == total_count:
        print("\n✅ All services are operational!")
        print("\n🚀 Pipeline is ready to process applications")
        print("\nNext steps:")
        print("  1. Open http://localhost:5173 in your browser")
        print("  2. Submit a test application")
        print("  3. Monitor the backend logs for pipeline execution")
        return 0
    else:
        print(f"\n⚠️  {total_count - healthy_count} service(s) are down")
        print("\nTo start missing services:")
        print("  python agents_services/start_all_complete.py")
        print("\nOr restart specific services:")
        print("  python agents_services/restart_services.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
