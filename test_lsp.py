"""Test LSP server command handlers via TCP."""
import json
import socket
import struct

def send_lsp_request(method, params):
    """Send LSP request and return response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 8473))
    
    # Build JSON-RPC 2.0 request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    body = json.dumps(request)
    content_length = len(body.encode('utf-8'))
    
    # LSP header + body
    message = f"Content-Length: {content_length}\r\n\r\n{body}"
    
    sock.send(message.encode('utf-8'))
    
    # Read response
    response = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        except:
            break
    
    sock.close()
    return response.decode('utf-8', errors='ignore')

# Test 1: Initialize
print("=== Test 1: Initialize ===")
resp = send_lsp_request("initialize", {
    "processId": None,
    "rootPath": None,
    "capabilities": {}
})
print(resp[:500])

# Test 2: Check executeCommandProvider in capabilities
if "executeCommandProvider" in resp:
    print("✓ executeCommandProvider found in capabilities")
    if "speakline.recordAtCursor" in resp:
        print("✓ speakline.recordAtCursor in commands")
    if "speakline.transcribeOnly" in resp:
        print("✓ speakline.transcribeOnly in commands")
else:
    print("✗ executeCommandProvider not found")

