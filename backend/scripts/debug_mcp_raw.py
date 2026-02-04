
import subprocess
import os
import sys
import time
import json
from dotenv import load_dotenv

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(backend_dir, ".env"))

def debug_mcp_raw():
    server_path = os.environ.get("MCP_YAML_SERVER_PATH")
    if not server_path:
        server_path = r"D:\My Code\Enable\domain_pack_Gen\domain-pack-mcp\mcp_server\main.py"

    server_dir = os.path.dirname(server_path)
    python_exe = os.path.join(server_dir, ".venv", "Scripts", "python.exe")
    
    print(f"Debugger: Starting {python_exe} {server_path}")
    
    env = os.environ.copy()
    env["FASTMCP_NO_BANNER"] = "1"
    env["FASTMCP_QUIET"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    
    process = subprocess.Popen(
        [python_exe, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=0 # Unbuffered for precise testing
    )
    
    # Non-blocking stderr reader
    import threading
    def read_stderr():
        try:
            for line in process.stderr:
                print(f"SERVER STDERR: {line.strip()}")
        except: pass
            
    t = threading.Thread(target=read_stderr, daemon=True)
    t.start()
    
    print("Debugger: Waiting 2s for server startup...")
    time.sleep(2)
    
    # Send initialize request
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    print(f"Debugger: Sending initialize request: {json.dumps(init_req)}")
    process.stdin.write(json.dumps(init_req) + "\n")
    process.stdin.flush()
    
    print("Debugger: Waiting 3s for response...")
    time.sleep(3)
    
    print("Debugger: Terminating and collecting output...")
    process.terminate()
    stdout, stderr = process.communicate()
    
    print("\n=== RAW STDOUT ===")
    print(stdout)
    print("\n=== RAW STDERR (collected on exit) ===")
    print(stderr)
    print("==================")

if __name__ == "__main__":
    debug_mcp_raw()
