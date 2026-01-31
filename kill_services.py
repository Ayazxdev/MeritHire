import subprocess
import os
import signal

def kill_port(port):
    try:
        # Find PID using netstat
        cmd = f'netstat -ano | findstr LISTENING | findstr :{port}'
        output = subprocess.check_output(cmd, shell=True).decode()
        
        for line in output.strip().split('\n'):
            if f':{port}' in line:
                pid = line.strip().split()[-1]
                print(f"Killing process {pid} on port {port}...")
                # Kill process on Windows
                subprocess.run(['taskkill', '/F', '/T', '/PID', pid], capture_output=True)
                return True
    except Exception as e:
        # print(f"No process found on port {port} or error: {e}")
        pass
    return False

if __name__ == "__main__":
    # Common ports for this project
    ports = range(8000, 8011)
    for port in ports:
        kill_port(port)
    
    # Also kill common frontend ports just in case
    kill_port(5173) 
    kill_port(3000)

    print("Agent services and ports have been cleared.")
