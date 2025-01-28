import subprocess
import time
import sys

def main():
    while True:
        proc = subprocess.Popen([sys.executable, "main.py"])
        exit_code = proc.wait()
        
        if exit_code == 100:  # Normal exit code
            print("Application closed normally")
            break
            
        print(f"Application crashed with exit code {exit_code}. Restarting...")
        time.sleep(2)  # Add delay before restarting to prevent tight loops

if __name__ == "__main__":
    main()