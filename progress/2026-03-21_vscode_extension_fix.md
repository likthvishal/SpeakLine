# VS Code Extension Fix - 2026-03-21

## Problem
VS Code extension was activating but LSP server couldn't be found or executed when spawned as child process from extension. Commands sent to LSP resulted in "Invalid Params: Command name 'speakline.recordAtCursor' is not defined" errors.

## Root Causes Identified
1. **Subprocess spawning failed**: `python -m speakline.lsp` couldn't find module from extension context
2. **Command handler registration broken**: Used `@server.feature(types.WORKSPACE_EXECUTE_COMMAND)` which isn't the correct pygls API

## Solution Implemented
1. **Switch to TCP mode**: Changed extension to connect to LSP server via TCP (port 8471) instead of spawning subprocess
   - Server runs: `python -m speakline.lsp --tcp 8471`
   - Extension connects: `new net.Socket()` → TCP localhost:8471
   - Config reads port from `lspPort` setting (default 8471)

2. **Fixed command registration**: Replaced decorator pattern with proper pygls API
   - Old: `@server.feature(types.WORKSPACE_EXECUTE_COMMAND)`
   - New: `@server.command("speakline.recordAtCursor")` etc. (separate decorator per command)
   - Created 4 command handlers: `cmd_record_at_cursor`, `cmd_record_at_cursor_preview`, `cmd_transcribe_only`, `cmd_insert_comment`

3. **Fixed null lspPort config**: Added explicit fallback in extension
   ```typescript
   const lspPort = config.get<number | null>("lspPort") ?? 8471;
   ```

## Files Changed
- `vscode-extension/src/extension.ts`: TCP connection mode, null coalescing for port
- `speakline/lsp/server.py`: Replaced command handler decorator pattern with pygls `@server.command()` API

## Verification
- LSP server starts successfully on port 8471
- Extension activates and connects to TCP server
- Commands are registered: `executeCommandProvider` lists all 4 commands
- Ready for functional testing (recording, transcribing, comment insertion)

## Next Steps
- Test Ctrl+Shift+R in Extension Development Host
- Verify recording + transcription flow works end-to-end
- Test comment insertion into files
