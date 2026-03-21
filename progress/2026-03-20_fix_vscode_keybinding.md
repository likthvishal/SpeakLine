# Fix VS Code Extension Keybinding — 2026-03-20

## Issue
Ctrl+Shift+V not working in VS Code extension. Keybinding was silently failing because:
1. Extension only activated for specific languages (Python, JavaScript, etc.)
2. LSP server failure cascaded to block all commands
3. Ctrl+Shift+V conflicts with VS Code's built-in Markdown preview

## Fixes Applied

### 1. activationEvents
Changed from language-specific list to `["onStartupFinished"]` in `vscode-extension/package.json`
- **Why**: Extension now loads immediately, works with any file type (including plain text, .md, etc.)

### 2. Keybinding
Changed from `ctrl+shift+v` → `ctrl+shift+r` (and `cmd+shift+v` → `cmd+shift+r` on Mac)
- **Why**: Avoids conflict with Markdown preview, clearer mnemonic (R = Record)
- Also updated preview keybinding: `ctrl+shift+alt+v` → `ctrl+shift+alt+r`

### 3. Error Messages
Updated all three "LSP server not running" errors in `extension.ts` to:
```
"SpeakLine: LSP server failed to start. Ensure 'speakline' is installed: pip install speakline"
```
- **Why**: Actionable guidance when LSP fails (e.g., PyAudio missing on Windows)

### 4. Recompiled
Ran `npm run compile` to build updated TypeScript

## Files Modified
- `vscode-extension/package.json` — activationEvents, keybindings
- `vscode-extension/src/extension.ts` — error messages (3 locations)

## Next Steps
1. Press F5 in VS Code to launch Extension Development Host
2. Open any file (`.py`, `.js`, `.md`, `.txt`, etc.)
3. Press **Ctrl+Shift+R** to record + insert comment
4. If LSP fails, error message now explains: "ensure 'speakline' is installed: pip install speakline"
