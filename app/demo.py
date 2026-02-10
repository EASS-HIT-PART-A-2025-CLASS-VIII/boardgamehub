import time
import subprocess
import os

def print_header(msg):
    print(f"\n{'='*60}")
    print(f" {msg}")
    print(f"{'='*60}\n")

def run_command(command, cwd=None, background=False):
    print(f"Running: {command}")
    if background:
        # For background processes like API/Streamlit
        if os.name == 'nt': # Windows
            return subprocess.Popen(command, shell=True, cwd=cwd)
        else:
            return subprocess.Popen(command.split(), cwd=cwd)
    else:
        # For synchronous commands
        subprocess.run(command, shell=True, check=True, cwd=cwd)

def main():
    print_header("🎲 BoardGameHub Demo Script - Requirement for EX3")
    
    # 1. Start Backend API
    print("Step 1: Starting Backend API...")
    api_process = run_command("uv run uvicorn app.main:app --port 8000", background=True)
    
    print("Waiting for API to initialize (5s)...")
    time.sleep(5)
    
    # 2. Start Frontend Dashboard
    print("Step 2: Starting Frontend Dashboard...")
    dashboard_process = run_command("uv run streamlit run frontend/dashboard.py", background=True)
    
    print("Waiting for Dashboard to initialize (5s)...")
    time.sleep(5)
    
    print_header("✅ Demo Running!")
    print("1. API is live at: http://127.0.0.1:8000/docs")
    print("2. Dashboard is live at: http://localhost:8501")
    print("\nInstructions for Demo:")
    print("- Go to the Dashboard.")
    print("- Use 'Upload CSV' to import games.")
    print("- Check the 'Stats' endpoint or top metrics.")
    print("\n(Press Ctrl+C to stop the demo)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping demo...")
        api_process.terminate()
        dashboard_process.terminate()
        print("Demo stopped.")

if __name__ == "__main__":
    main()
