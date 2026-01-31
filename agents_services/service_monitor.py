"""
Service Health Monitor and Auto-Recovery

Monitors all agent services and automatically restarts failed services.
This ensures the pipeline stays operational even if individual services crash.
"""
import time
import urllib.request
import urllib.error
import subprocess
import sys
import os
from typing import Dict, List, Tuple

# Import centralized configuration
try:
    from ports_config import PORTS, SERVICE_FILES, HEALTH_ENDPOINTS
except ImportError:
    print("ERROR: ports_config.py not found!")
    sys.exit(1)


class ServiceMonitor:
    """Monitors and auto-recovers agent services"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.processes: Dict[str, subprocess.Popen] = {}
        self.failure_counts: Dict[str, int] = {}
        self.max_failures = 3
    
    def check_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        url = HEALTH_ENDPOINTS.get(service_name)
        if not url:
            return False
        
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a failed service"""
        script = SERVICE_FILES.get(service_name)
        port = PORTS.get(service_name)
        
        if not script or not port:
            print(f"[ERROR] Unknown service: {service_name}")
            return False
        
        print(f"[RECOVERY] Restarting {service_name} on port {port}...")
        
        # Kill old process if exists
        if service_name in self.processes:
            try:
                self.processes[service_name].terminate()
                self.processes[service_name].wait(timeout=5)
            except Exception:
                pass
        
        # Kill process on port (Windows)
        try:
            result = subprocess.run(
                f'netstat -ano | findstr ":{port}"',
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if 'LISTENING' in line:
                        pid = line.split()[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                        time.sleep(1)
        except Exception as e:
            print(f"[WARN] Could not kill process on port {port}: {e}")
        
        # Start new process
        try:
            py = sys.executable
            proc = subprocess.Popen(
                [py, script],
                cwd=os.path.join(os.path.dirname(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.processes[service_name] = proc
            
            # Wait for service to start
            time.sleep(3)
            
            # Verify it's healthy
            if self.check_health(service_name):
                print(f"[SUCCESS] {service_name} restarted successfully")
                self.failure_counts[service_name] = 0
                return True
            else:
                print(f"[WARN] {service_name} started but health check failed")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to restart {service_name}: {e}")
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("=" * 80)
        print("Service Health Monitor Started")
        print(f"Checking every {self.check_interval} seconds")
        print("=" * 80)
        
        while True:
            try:
                print(f"\n[{time.strftime('%H:%M:%S')}] Health Check...")
                
                all_healthy = True
                for service_name in PORTS.keys():
                    if service_name == "MCP":  # Skip MCP for now
                        continue
                    
                    is_healthy = self.check_health(service_name)
                    
                    if is_healthy:
                        status = "✓ OK"
                        self.failure_counts[service_name] = 0
                    else:
                        status = "✗ FAILED"
                        all_healthy = False
                        
                        # Track failures
                        self.failure_counts[service_name] = self.failure_counts.get(service_name, 0) + 1
                        
                        # Auto-restart if below max failures
                        if self.failure_counts[service_name] <= self.max_failures:
                            print(f"  {service_name:15} {status} - Attempting recovery...")
                            self.restart_service(service_name)
                        else:
                            print(f"  {service_name:15} {status} - Max failures reached, manual intervention required")
                    
                    if is_healthy or self.failure_counts[service_name] > self.max_failures:
                        print(f"  {service_name:15} {status}")
                
                if all_healthy:
                    print("  All services healthy ✓")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n\nMonitor stopped by user")
                break
            except Exception as e:
                print(f"[ERROR] Monitor error: {e}")
                time.sleep(5)


def main():
    monitor = ServiceMonitor(check_interval=30)
    monitor.monitor_loop()


if __name__ == "__main__":
    main()
