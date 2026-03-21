"""Test LSP command handlers."""
import json
import socket
import time
import os
import tempfile
import sys

# Fix unicode on Windows
sys.stdout.reconfigure(encoding='utf-8')

def send_lsp_message(sock, method, params, msg_id=1):
    """Send LSP message and receive response."""
    request = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": method,
        "params": params
    }
    body = json.dumps(request)
    message = f"Content-Length: {len(body)}\r\n\r\n{body}"
    sock.send(message.encode())
    
    # Read response header
    header = b''
    while b'\r\n\r\n' not in header:
        chunk = sock.recv(1024)
        if not chunk:
            return None
        header += chunk
    
    # Parse Content-Length
    lines = header.split(b'\r\n')
    content_length = 0
    for line in lines:
        if line.startswith(b'Content-Length:'):
            content_length = int(line.split(b':')[1].strip())
            break
    
    # Read body
    body_start = header.find(b'\r\n\r\n') + 4
    body = header[body_start:body_start + content_length]
    
    return json.loads(body)

# Connect to LSP
print("Connecting to LSP on port 8473...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 8473))
print("[OK] Connected")

# Test 1: Initialize
print("\n=== Test 1: Initialize (check capabilities) ===")
resp = send_lsp_message(sock, "initialize", {
    "processId": None,
    "rootPath": None,
    "capabilities": {}
})

if resp and "result" in resp:
    result = resp["result"]
    if "capabilities" in result:
        caps = result["capabilities"]
        if "executeCommandProvider" in caps:
            commands = caps["executeCommandProvider"].get("commands", [])
            print(f"[OK] executeCommandProvider found")
            print(f"     Commands: {commands}")
            
            required = [
                "speakline.recordAtCursor",
                "speakline.recordAtCursorPreview", 
                "speakline.transcribeOnly",
                "speakline.insertComment"
            ]
            
            for cmd in required:
                if cmd in commands:
                    print(f"     [OK] {cmd}")
                else:
                    print(f"     [FAIL] {cmd} MISSING")
        else:
            print("[FAIL] executeCommandProvider not found")
    else:
        print("[FAIL] capabilities not found in result")
else:
    print(f"[FAIL] No response or error: {resp}")

# Test 2: Create a temp file for testing
print("\n=== Test 2: insertComment command ===")
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write("def hello():\n    pass\n")
    temp_file = f.name

try:
    file_uri = f"file:///{temp_file.replace(chr(92), '/')}"
    params = {
        "command": "speakline.insertComment",
        "arguments": [file_uri, 0, "# This is a test comment"]
    }
    
    resp = send_lsp_message(sock, "workspace/executeCommand", params)
    
    if resp:
        if "error" in resp:
            print(f"[FAIL] Command failed: {resp['error']}")
        elif "result" in resp:
            print(f"[OK] Command executed")
            result = json.loads(resp["result"]) if isinstance(resp["result"], str) else resp["result"]
            print(f"     Response: {result}")
            
            # Check if file was modified
            with open(temp_file, 'r') as f:
                content = f.read()
                if "# This is a test comment" in content:
                    print(f"[OK] Comment inserted in file")
                else:
                    print(f"[FAIL] Comment not found in file")
                    print(f"     Content:\n{content}")
    else:
        print("[FAIL] No response from command")
        
finally:
    os.unlink(temp_file)

sock.close()
print("\n=== Test Complete ===")
