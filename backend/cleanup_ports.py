
import os
import subprocess
import signal
import time

ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010]

def kill_port(port):
    print(f"Checking port {port}...")
    try:
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in output.splitlines():
            if "LISTENING" in line:
                pid = line.strip().split()[-1]
                print(f"Killing PID {pid} on port {port}...")
                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
    except subprocess.CalledProcessError:
        print(f"Port {port} is free.")

if __name__ == "__main__":
    for p in ports:
        kill_port(p)
    print("Cleanup complete.")
