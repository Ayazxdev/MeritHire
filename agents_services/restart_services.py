"""
Restart Specific Services Script

Restarts only the services that need to be reloaded after code changes.
This is faster than restarting all services.
"""
import subprocess
import sys
import os
import time

def kill_process_on_port(port: int):
    """Kill any process running on the specified port (Windows)"""
    try:
        # Find process on port
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    pid = parts[-1]
                    print(f"Killing process {pid} on port {port}")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                    time.sleep(0.5)
                    return True
        return False
    except Exception as e:
        print(f"Error killing process on port {port}: {e}")
        return False

def start_service(script_name: str, port: int):
    """Start a service"""
    py = sys.executable
    print(f"Starting {script_name} on port {port}...")
    
    proc = subprocess.Popen(
        [py, script_name],
        cwd=os.path.dirname(__file__),
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
    
    time.sleep(2)  # Give it time to start
    return proc

def main():
    print("=" * 80)
    print("Restarting Modified Services")
    print("=" * 80)
    
    # Services that were modified or needs check
    services_to_restart = [
        ("passport_service.py", 8010),
        ("github_service.py", 8005),
        ("start_mcp.py", 8011),
        ("matching_agent_service.py", 8003),
    ]

    
    for script, port in services_to_restart:
        print(f"\n[{script}]")
        print(f"  1. Stopping service on port {port}...")
        kill_process_on_port(port)
        
        print(f"  2. Starting service...")
        start_service(script, port)
        
        print(f"  ✓ Service restarted on port {port}")
    
    print("\n" + "=" * 80)
    print("All services restarted successfully!")
    print("=" * 80)
    print("\nServices are running in separate console windows.")
    print("Check the backend logs to verify the pipeline works.")

if __name__ == "__main__":
    main()
