# Quick Start: Testing the LSP Extension

## Status Summary ✅

| Component | Status | Notes |
|-----------|--------|-------|
| LSP Server | ✅ Running | Port 8473, all 4 commands registered |
| Core Features | ✅ Tested | VoiceCommenter + MockTranscriber working |
| Extension | ✅ Compiled | TypeScript → JavaScript compiled successfully |
| TCP Connection | ✅ Ready | Extension connects to LSP on port 8473 |

---

## Quick Test (5 minutes)

### Step 1: Ensure LSP Server Running
```bash
# Terminal 1 - Keep running
python -m speakline.lsp --tcp 8473 --log lsp.log
```

Verify:
```bash
netstat -ano | grep 8473  # Should show LISTENING on port 8473
```

### Step 2: Launch Extension
```bash
# Terminal 2 - In vscode-extension directory
npm run watch    # Builds on file changes (leave running)
```

### Step 3: Start Debugging
```bash
# VS Code window 1 - Extension Development Host
Press F5  # Or Run → Start Debugging
```

A new VS Code window will open with the extension loaded.

### Step 4: Test Recording
In the new VS Code window:
1. **Open a Python file** (any .py file)
2. **Place cursor on any line**
3. **Press Ctrl+Shift+R** to record
4. **Expected**:
   - Status bar shows "$(loading~spin) Recording..."
   - After 3 seconds: Comment inserted at cursor
   - Comment text: "Mock transcribed comment" (using MockTranscriber)

---

## Test Commands (Command Palette)

1. **Record at Cursor**
   - `Ctrl+Shift+P` → "SpeakLine: Record Comment at Cursor"
   - Shortcut: `Ctrl+Shift+R`

2. **Record with Preview**
   - `Ctrl+Shift+P` → "SpeakLine: Record Comment (Preview)"
   - Shows comment before inserting

3. **Transcribe Only**
   - `Ctrl+Shift+P` → "SpeakLine: Transcribe Only"
   - Returns text without editing file

4. **Insert Comment**
   - `Ctrl+Shift+P` → "SpeakLine: Insert Comment"
   - Manual comment input

---

## What's Being Tested

### Extension Features
- ✅ Activation message appears
- ✅ Status bar shows "(mic) SpeakLine"
- ✅ TCP connection to LSP server (port 8473)
- ✅ Keybinding Ctrl+Shift+R triggers recording
- ✅ Error messages if LSP unavailable

### LSP Commands
- ✅ `speakline.recordAtCursor` — records & inserts
- ✅ `speakline.recordAtCursorPreview` — preview before insert
- ✅ `speakline.transcribeOnly` — transcribe without editing
- ✅ `speakline.insertComment` — direct text insertion

### VoiceCommenter (Backend)
- ✅ MockTranscriber returns fixed text
- ✅ Comment insertion respects indentation
- ✅ Language detection from file extension
- ✅ File I/O works correctly

---

## Troubleshooting

### "Cannot connect to LSP server on port 8473"
**Solution**:
```bash
# Check if port is in use
netstat -ano | grep 8473

# Kill existing process if needed
taskkill /PID <PID> /F

# Restart LSP server
python -m speakline.lsp --tcp 8473
```

### Extension not loading
**Solution**:
```bash
# Rebuild
npm run compile

# Restart debugging (Ctrl+Shift+D)
```

### LSP server crashes
**Solution**:
```bash
# Check logs
tail -f lsp.log

# Restart with verbose logging
python -m speakline.lsp --tcp 8473 --log lsp_debug.log
```

### Comment not inserting
**Solution**:
1. Check LSP logs: `tail lsp.log`
2. Verify file is writable
3. Check Output panel in VS Code for errors

---

## File Structure

```
audiocomments/
├── vscode-extension/
│   ├── src/extension.ts          (Extension entry point)
│   ├── package.json              (Extension manifest)
│   ├── tsconfig.json             (TypeScript config)
│   └── dist/                     (Compiled JavaScript)
├── speakline/
│   ├── lsp/
│   │   ├── server.py             (LSP server + handlers)
│   │   ├── __main__.py           (Entry point)
│   ├── commenter.py              (VoiceCommenter class)
│   ├── transcriber.py            (MockTranscriber)
│   └── formatter.py              (Comment formatting)
```

---

## Test Results Logged

All test results are logged to:
- `progress/2026-03-21_lsp_features_test.md` — Detailed test report
- `progress/2026-03-21_TESTING_GUIDE.md` — This file

---

## Next Steps After Testing

1. **Manual QA**: Follow the quick test above
2. **File Verification**: Check that comments are inserted correctly
3. **Error Handling**: Test with LSP server stopped
4. **Real Recording**: Switch to WhisperTranscriber if audio hardware available
5. **Package**: `npm run package` to create .vsix extension file

---

**Ready to test? Start LSP server in Terminal 1, then press F5 in VS Code!**
