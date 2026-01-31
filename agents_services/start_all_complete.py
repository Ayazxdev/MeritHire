"""
Start All Agent Services (Complete Pipeline)
Utility script to start all 11 agent services simultaneously.

IMPORTANT: All ports are now centralized in ports_config.py
DO NOT hardcode ports here - they are imported from the config!
"""
import subprocess
import sys
import os
import time
import urllib.request
import urllib.error

# Import centralized port configuration
try:
    from ports_config import PORTS, SERVICE_FILES, HEALTH_ENDPOINTS, PIPELINE_STAGES
except ImportError:
    print("ERROR: ports_config.py not found!")
    print("Please ensure ports_config.py exists in the agents_services directory.")
    sys.exit(1)

def _python_bin() -> str:
    return os.environ.get("AGENT_PYTHON") or sys.executable

def _wait_health(url: str, timeout_s: int = 20) -> None:
    deadline = time.time() + timeout_s
    last_err = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    raise RuntimeError(f"Health check failed for {url}: {last_err}")

def start_service(script_name: str, port: int) -> subprocess.Popen:
    """Start a service in a separate process and return the process handle."""
    py = _python_bin()
    print(f"Starting {script_name} on port {port} using: {py}")
    return subprocess.Popen(
        [py, script_name],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

def _drain_output(p: subprocess.Popen, max_lines: int = 200) -> str:
    if not p.stdout:
        return ""
    lines = []
    start = time.time()
    while time.time() - start < 1.0:
        line = p.stdout.readline()
        if not line:
            break
        lines.append(line.rstrip("\n"))
        if len(lines) >= max_lines:
            break
    return "\n".join(lines)

def main():
    print("=" * 80)
    print("Starting All Agent Services - Complete Pipeline (11 Services)")
    print("=" * 80)

    processes: list[subprocess.Popen] = []

    # Build services list from centralized config
    services = [
        (SERVICE_FILES[name], PORTS[name], HEALTH_ENDPOINTS[name])
        for name, _ in PIPELINE_STAGES
    ]

    try:
        for script, port, health in services:
            p = start_service(script, port)
            processes.append(p)

            # Give the process a moment to import + bind
            time.sleep(0.8)

            # If it already exited, show logs and abort
            if p.poll() is not None:
                out = _drain_output(p)
                raise RuntimeError(
                    f"{script} exited early with code {p.returncode}.\n"
                    f"--- last output ---\n{out}\n-------------------"
                )

            # Wait until health endpoint responds
            _wait_health(health, timeout_s=20)

        print("\n" + "=" * 80)
        print("All services are up [OK]")
        print("=" * 80)
        print("\nPIPELINE STAGES:\n")
        
        # Display all stages from centralized config
        for name, description in PIPELINE_STAGES:
            port = PORTS[name]
            print(f"{description:40} http://localhost:{port}")
        
        print("=" * 80)
        print("\nPress Ctrl+C to stop all services\n")

        # Block until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping all services...")
    except Exception as e:
        print("\n[ERROR] Failed to start agent services.")
        print(str(e))
    finally:
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        
        # Wait a moment for clean shutdown
        time.sleep(1)
        print("\nAll services stopped. Goodbye!")

if __name__ == "__main__":
    main()