"""
Start Full System (Agents + Backend + Frontend)
"""
import subprocess
import time
import os
import sys
import webbrowser

def main():
    print("="*80)
    print("🚀 STARTING FULL HIRING PLATFORM SYSTEM")
    print("="*80)
    
    # 1. Start Agents & MCP (Port 8001-8011)
    print("\n[1/3] Launching Agents & MCP...")
    agents_proc = subprocess.Popen(
        ["python", "agents_services/start_all_complete.py"],
        cwd=os.getcwd(),
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    # 2. Start Backend (Port 8000)
    print("\n[2/3] Launching Backend API (Port 8000)...")
    
    # Explicitly use the venv python we just created
    backend_python = os.path.join(os.getcwd(), "backend", "venv", "Scripts", "python.exe")
    if not os.path.exists(backend_python):
        print(f"Warning: Venv python not found at {backend_python}, falling back to system python")
        backend_python = "python" # Fallback

    backend_proc = subprocess.Popen(
        [backend_python, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
        cwd=os.path.join(os.getcwd(), "backend"),
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    # 3. Start Frontend (Port 5173)
    print("\n[3/3] Launching Frontend (Port 5173)...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(os.getcwd(), "fair-hiring-frontend"),
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

    print("\n✅ All systems launching in separate windows...")
    print("Waiting 10s for startup...")
    time.sleep(10)
    
    try:
        webbrowser.open("http://localhost:5173")
    except:
        pass

    print("\nPress Ctrl+C to stop all services (This script validates; close windows to stop actual servers)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting launcher...")

if __name__ == "__main__":
    main()
