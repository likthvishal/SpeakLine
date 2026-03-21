# Background HTTP Daemon Implementation - 2026-03-21

## Problem
pygls LSP server exits immediately after initialization (code 0). After 6+ hours debugging, determined root cause is pygls library's `server.start_io()` lifecycle issue.

## Solution
Replace LSP entirely with simple HTTP daemon on port 7777.

## Files Created
1. **speakline/daemon.py** (272 lines)
   - HTTP JSON API server using `http.server.HTTPServer`
   - Four endpoints: `/record`, `/preview`, `/transcribe`, `/insert`
   - Endpoint `/health` for readiness checking
   - All responses: `{"ok": true|false, "error": "...", ...}`
   - Reuses `VoiceCommenter` singleton + URI path conversion
   - Threading lock prevents concurrent recording
   - All errors caught and returned as JSON

## Files Modified
1. **vscode-extension/src/extension.ts**
   - Removed: `LanguageClient`, `ServerOptions`, LSP imports
   - Added: `child_process`, `http` modules
   - New: `startDaemon()` - spawns daemon, waits for health check (10s timeout)
   - New: `sendCommand()` - HTTP POST wrapper to `127.0.0.1:7777`
   - Updated: All command functions to use `sendCommand()` instead of `client.sendRequest()`
   - Updated: `deactivate()` kills daemon process
   - Removed: All `client` variable references
   - Compiler: TypeScript passes ✓

2. **vscode-extension/package.json**
   - Removed: `vscode-languageclient` dependency
   - Removed: Dead `speakline.lspPort` config

## Testing
```bash
# Daemon starts
python -m speakline.daemon --port 7777
# Output: INFO:__main__:Starting SpeakLine daemon on port 7777

# Health endpoint works
curl -X POST http://127.0.0.1:7777/health -d '{}'
# Response: {"ok": true, "status": "ready"}
```

## Next Steps
1. Test in VS Code (F5 debug)
2. Test `Ctrl+Shift+R` to record
3. Test preview/accept flow
4. Test insertComment command
5. Verify daemon kills on extension deactivate

## Key Design Decisions
- Fixed port 7777: Simplest for MVP (no discovery needed)
- HTTP over raw TCP: Easy to debug with curl
- Detached daemon process: Won't block extension
- Health check polling: Extension waits up to 10s for daemon ready
- JSON responses: All endpoints return `{"ok": true/false, ...}`

## Commit
Hash: e3bfc37
Message: "refactor: replace LSP with background HTTP daemon"
