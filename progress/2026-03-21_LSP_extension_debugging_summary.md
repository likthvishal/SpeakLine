# VSCode LSP Extension Debugging Session - 2026-03-21

## Summary
Spent 6+ hours debugging VSCode extension with pygls LSP server integration. Applied async/await fix to extension lifecycle. Identified but could not resolve root blocker: pygls `server.start_io()` causes subprocess to exit immediately after initialization (exit code 0).

## Changes Made
1. **extension.ts:13** - Made `activate()` async and await LSP connection
2. **extension.ts:51** - Changed `startLanguageServer()` to return Promise<void>
3. **server.py** - Attempted custom `@server.feature(types.EXIT)` handler (removed, didn't work)
4. Switched from TCP mode (port 8473) to stdio subprocess mode

## Root Cause Identified
- pygls library's `server.start_io()` method exits immediately after responding to LSP initialize request
- Does not enter the continuous stdin-listening message loop required by LSP protocol
- Affects both TCP and stdio communication modes
- Custom exit handler cannot intercept pygls' sys.exit() call

## Blocker (Unresolved)
```
[Error - HH:MM AM] Server process exited with code 0
```
Occurs immediately after:
```
✓ SpeakLine LSP initialized
```

## Attempts That Failed
- Custom exit handler in server.py
- TCP mode explicit lifecycle management
- Removing subprocess options from ServerOptions
- Various timing tweaks in extension activation

## Next Steps for Future Sessions
1. Investigate pygls source code — why does `start_io()` exit?
2. Test raw JSON-RPC over stdio (without pygls abstraction)
3. Consider background daemon architecture instead of extension-tied process
4. Alternative: Direct Python function calls, no LSP layer

## Files Modified
- vscode-extension/src/extension.ts
- speakline/lsp/server.py

## Commit
- Commit hash: (see git log)
- Message: Documents async/await fix + switches to stdio mode with TODO comment about pygls lifecycle

## Key Learnings
- Don't spend >2 hours on one communication mode without pivoting to alternatives
- pygls may not be the right fit for this simple use case
- Async/await pattern fix is solid and should be kept
- Layer-based testing (compile → startup → protocol → lifecycle) is most effective debugging approach
