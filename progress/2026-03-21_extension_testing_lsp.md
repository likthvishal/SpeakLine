# 2026-03-21 Extension Testing & LSP Debugging

## Status
VS Code extension is activating correctly, but **LSP server command handlers are not implemented**. Extension connects to LSP on port 8472 but server responds with "command not found" errors.

## Issues Found
1. **LSP server missing command handlers** — `speakline.recordAtCursor`, `speakline.recordAtCursorPreview`, `speakline.transcribeOnly`, `speakline.insertComment` are not registered
2. **Port conflicts** — Previous LSP processes left sockets open (8471, 8472). Had to kill PIDs 22628, 28696 to free ports.
3. **LSP server exiting immediately** — Server starts briefly then crashes. Need to investigate `speakline\lsp\server.py` for command handler registration.

## What Works
- Extension activates on startup ✓
- Extension connects to LSP on port 8472 ✓
- Keybinding Ctrl+Shift+R is registered ✓
- Status bar icon shows ✓

## What Doesn't Work
- Commands fail with "Invalid Params: Command name 'speakline.recordAtCursor' is not defined"
- LSP server process exits after starting (needs investigation)

## Next Steps
1. Add command handlers to `speakline/lsp/server.py` using `@server.command()` decorator
2. Keep LSP server running (background process or use `nohup`)
3. Test Ctrl+Shift+R again with handlers in place
4. If still failing, check for errors in Extension Development Host logs
